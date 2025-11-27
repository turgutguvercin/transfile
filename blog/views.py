from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from django.utils import translation

from .models import Blog


def blog_list(request):
    current_lang = translation.get_language()
    # Get only blogs that have translations in the current language
    blogs = Blog.objects.filter(
        translations__language_code=current_lang
    ).prefetch_related('translations').order_by("-date")
    paginator = Paginator(blogs, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "blogs/blog_list.html", {"blogs": page_obj})

def blog_detail(request, slug):
    current_lang = translation.get_language()
    blog = get_object_or_404(Blog.objects.language(current_lang), translations__slug=slug)
    return render(request, "blogs/blog_detail.html", {"blog":blog}) 
