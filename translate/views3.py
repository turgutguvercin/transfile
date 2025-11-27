from decimal import Decimal
import os
import tempfile
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction
from django.http import HttpResponse, FileResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.conf import settings
from celery.result import AsyncResult

from .utils.text_length_calculator import calculate_length
from .utils.price_calculator import calculate_price
from .forms import UploadFileForm
from .tasks import translate_file_task
from django.contrib.auth.decorators import login_required
from wallet.models import UserWallet
from documents.models import Document
from django.utils import timezone


MAX_UPLOAD_SIZE = 25 * 1024 * 1024  # 25 MB

def home(request):
    """
    Home page view - landing page for the translation service
    """
    return render(request, "translate/home.html")

@login_required
def upload_file(request):
    """
    Main upload view - now supports both traditional and chunked uploads
    """


    return render(request, "translate/upload.html")



@csrf_exempt
@require_http_methods(["POST"])
def chunked_upload(request):
    """
    Handle chunked file uploads
    """
    try:
        chunk_number = int(request.POST.get('chunk_number', 0))
        total_chunks = int(request.POST.get('total_chunks', 1))
        file_name = request.POST.get('file_name', 'unknown')
        upload_id = request.POST.get('upload_id')
        chunk_start = int(request.POST.get('chunk_start', -1))
        chunk_size = int(request.POST.get('chunk_size', 0))
        
        if not all([upload_id, file_name]):
            return JsonResponse({'error': 'Missing required parameters'}, status=400)
        
        if 'chunk' not in request.FILES:
            return JsonResponse({'error': 'No chunk provided'}, status=400)
        
        chunk = request.FILES['chunk']
        
        # Ensure destination directory exists
        uploads_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        final_file_path = os.path.join(uploads_dir, f"{upload_id}_{file_name}")

        # Ensure file exists to allow r+b writes
        if not os.path.exists(final_file_path):
            open(final_file_path, 'wb').close()

        # Determine write offset
        if chunk_start < 0:
            # Fallback to sequential offset if not provided (may be incorrect with parallel uploads)
            chunk_start = 0 if chunk_size == 0 else chunk_number * chunk_size

        # Enforce max upload size using an accumulated byte counter in cache
        size_key = f'upload_{upload_id}_bytes'
        uploaded_bytes = cache.get(size_key, 0)
        uploaded_bytes += chunk.size
        if uploaded_bytes > MAX_UPLOAD_SIZE:
            # Cleanup cache and any partial file
            cache.delete(size_key)
            cache.delete(f'upload_{upload_id}_chunks')
            try:
                if os.path.exists(final_file_path):
                    os.remove(final_file_path)
            except Exception:
                pass
            return JsonResponse({'error': 'File exceeds maximum size of 25MB'}, status=413)

        cache.set(size_key, uploaded_bytes, timeout=3600)

        # Write chunk at exact offset to avoid corruption with parallel uploads
        with open(final_file_path, 'r+b') as f:
            f.seek(chunk_start)
            for data in chunk.chunks():
                f.write(data)


        
        # Store chunk metadata and translation parameters in cache
        cache_key = f'upload_{upload_id}_chunks'
        uploaded_chunks = cache.get(cache_key, set())
        uploaded_chunks.add(chunk_number)
        cache.set(cache_key, uploaded_chunks, timeout=3600)
        
        #Check if we now have all chunks        
        if len(uploaded_chunks) == total_chunks:
            cache.delete(cache_key)  # cleanup
            cache.delete(size_key)
            rel_path = os.path.join('uploads', f"{upload_id}_{file_name}")
            abs_path = os.path.join(settings.MEDIA_ROOT, rel_path)
            
            try:
                # Import here to avoid circular imports
                from .translator import detect_mime, MIME_MAPPINGS
                
                # Get file extension and check MIME type
                _, ext = os.path.splitext(file_name)
                ext = ext.lower()
                
                if ext not in MIME_MAPPINGS:
                    os.unlink(abs_path)
                    return JsonResponse({'error': f'Unsupported file type: {ext}'}, status=400)
                    
                mime = detect_mime(abs_path).lower()
                valid_mimes = [m.lower() for m in MIME_MAPPINGS[ext]]
                
                if mime not in valid_mimes:
                    os.unlink(abs_path)
                    return JsonResponse({
                        'error': f'The file format does not match its extension. Expected {ext} file but got {mime}.'
                    }, status=400)
                
                return JsonResponse({
                    'success': True,
                    'message': 'File upload completed',
                    'file_path': rel_path,
                    'completed': True
                })
                
            except Exception as e:
                # Clean up file if there's an error
                try:
                    os.unlink(abs_path)
                except:
                    pass
                raise

        return JsonResponse({
            'success': True,
            'message': f'Chunk {chunk_number + 1}/{total_chunks} uploaded',
            'uploaded_chunks': len(uploaded_chunks),
            'total_chunks': total_chunks,
            'completed': False
        })

    except Exception as e:
        return JsonResponse({'error': f'Upload failed: {str(e)}'}, status=500)






@login_required
@csrf_exempt
@require_http_methods(["POST"])
def start_translate(request):
    """
    Start the translation task from the saved file 
    """
    user = request.user
    try:

        file_path = request.POST.get("file_path")
        if not file_path:
            return JsonResponse({'error':'File could not found'})
        source_lang = request.POST.get("source_language")
        target_lang = request.POST.get("target_language")

        if not all([source_lang, target_lang]):
            return JsonResponse({'error':'Some parameters are missing :('}, status=400)

        # Resolve absolute/relative path
        if os.path.isabs(file_path):
            abs_path = file_path
        else:
            abs_path = os.path.join(settings.MEDIA_ROOT, file_path)
        if not os.path.exists(abs_path):
            return JsonResponse({'error': 'Uploaded file not found on server'}, status=404)

        text_length = calculate_length(abs_path)
        price = calculate_price(text_length)["price"]
        price = Decimal(str(price))

        try:
            with transaction.atomic():
                wallet = user.wallet
                try:
                    wallet.spend_credits(price, description="translation service")
                except ValueError as e:
                    # Insufficient credits or wallet validation error
                    return JsonResponse({'error': str(e)}, status=400)

                # Create document record
                # Keep relative path in DB for portability
                try:
                    rel_source_path = os.path.relpath(abs_path, settings.MEDIA_ROOT)
                except Exception:
                    rel_source_path = file_path

                document = Document.objects.create(
                    user=user,
                    source_file=rel_source_path,
                    source_language=source_lang,
                    target_language=target_lang,
                    status='processing'
                )

                # Start translation task directly since file is already saved
                task_id = start_translation_task(abs_path, source_lang, target_lang)
                document.task_id = task_id
                document.save()

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

        return JsonResponse({
            'success': True,
            'message': 'File has been translated successfully!',
            'task_id': task_id,
            'status_url': f'/upload/status/{task_id}/'
        })    

    except Exception as e:
        return JsonResponse({'error': f'Upload failed: {str(e)}'}, status=500)


def start_translation_task(file_path, source_language, target_language):
    """
    Start Celery translation task
    """
    # Build output file path similar to your original logic
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    ext = os.path.splitext(file_path)[1]
    tmp_out_path = os.path.join(os.path.dirname(file_path), f"{base_name}.{target_language[:2]}{ext}")
    
    # Start Celery task
    task = translate_file_task.delay(str(file_path), str(tmp_out_path), source_language, target_language)
    return task.id

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def direct_upload(request):
    """
    Handle direct uploads (for smaller files) and start translation
    """
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'}, status=400)

        uploaded_file = request.FILES['file']
        # Enforce size limit for direct uploads
        if uploaded_file.size > MAX_UPLOAD_SIZE:
            return JsonResponse({'error': 'File exceeds maximum size of 25MB'}, status=413)
            
        # Create a temporary file to validate MIME type
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)
            temp_path = temp_file.name
            
        try:
            # Import here to avoid circular imports
            from .translator import detect_mime, MIME_MAPPINGS
            import os
            
            # Get file extension and check MIME type
            _, ext = os.path.splitext(uploaded_file.name)
            ext = ext.lower()
            
            if ext not in MIME_MAPPINGS:
                os.unlink(temp_path)
                return JsonResponse({'error': f'Unsupported file type: {ext}'}, status=400)
                
            mime = detect_mime(temp_path).lower()
            valid_mimes = [m.lower() for m in MIME_MAPPINGS[ext]]
            
            if mime not in valid_mimes:
                os.unlink(temp_path)
                return JsonResponse({
                    'error': f'The file format does not match its extension. Expected {ext} file but got {mime}.'
                }, status=400)
                
            # If validation passes, save the file
            file_name = getattr(uploaded_file, 'name', 'uploaded_file')
            file_path = default_storage.save(f"uploads/{file_name}", ContentFile(open(temp_path, 'rb').read()))
            os.unlink(temp_path)
            
            return JsonResponse({
                'success': True,
                'message': 'File uploaded successfully',
                'file': file_path
            })
            
        except Exception as e:
            # Clean up temp file if there's an error
            try:
                os.unlink(temp_path)
            except:
                pass
            raise
        
    except Exception as e:
        return JsonResponse({'error': f'Upload failed: {str(e)}'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def get_price(request):

    filepath = request.POST.get("file_path")
    if not filepath:
        return JsonResponse({'error': 'file_path is required'}, status=400)

    # Resolve absolute vs relative
    full_path = filepath if os.path.isabs(filepath) else os.path.join(settings.MEDIA_ROOT, filepath)
    if not os.path.exists(full_path):
        return JsonResponse({'error': 'File not found'}, status=404)

    text_length = calculate_length(full_path)
    price = calculate_price(text_length)["price"]

    return JsonResponse({
        'price': price,
        'message': 'Estimated fee/price for the document that uploaded',
        'file': (os.path.relpath(full_path, settings.MEDIA_ROOT) if not os.path.isabs(filepath) else filepath), 

    })




@login_required
def download_file(request, task_id: str):
    """
    Download the translated file
    """
    res = AsyncResult(task_id)
    
    if not res.ready() or res.failed():
        return HttpResponse("File not ready or translation failed.", status=404)
    
    out_path = res.result
    
    if not os.path.exists(out_path):
        return HttpResponse("File not found.", status=404)
    
    filename = os.path.basename(out_path)
    return FileResponse(open(out_path, "rb"), as_attachment=True, filename=filename)


@require_http_methods(["GET"])
def ajax_task_status(request, task_id: str):
    """
    AJAX endpoint for checking task status
    """
    res = AsyncResult(task_id)
    
    try:
        document = Document.objects.get(task_id=task_id)
    except Document.DoesNotExist:
        return JsonResponse({'error': 'Document not found'}, status=404)
    
    if res.failed():
        document.status = 'failed'
        document.save()
        error_message = str(res.result) if res.result else 'Translation failed.'
        
        # Format MIME type validation errors to be more user-friendly
        if "Invalid MIME" in error_message:
            error_message = "The file format doesn't match its extension. Please make sure you're uploading a valid file."
            
        return JsonResponse({
            'status': 'FAILURE',
            'error': error_message
        }, status=500)
    
    if not res.ready():
        return JsonResponse({
            'status': 'PENDING',
            'message': 'Processing…',
            'progress': None  # You can add progress tracking if your task supports it
        })
    
    # Update document status and translated file path
    document.status = 'completed'
    # Convert absolute path to relative path for database storage
    try:
        translated_rel_path = os.path.relpath(res.result, settings.MEDIA_ROOT)
        document.translated_file = translated_rel_path
    except Exception:
        document.translated_file = res.result
    document.completed_at = timezone.now()
    document.save()
    
    return JsonResponse({
        'status': 'SUCCESS',
        'message': 'Translation completed',
        'download_url': f'/upload/download/{task_id}/'
    })

