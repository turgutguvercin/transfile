from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Document

@login_required
def get_history(request):
    user = request.user
    documents = Document.objects.filter(user=user).order_by('-uploaded_at')

    return render(request, 'documents/history.html', {"documents":documents})