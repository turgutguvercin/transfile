# urls.py
from django.urls import path
from . import views3

urlpatterns = [
      path('', views3.home, name='home'),
    path('upload/', views3.upload_file, name='upload_file'),
    path('upload/chunked/', views3.chunked_upload, name='chunked_upload'),
    path('upload/direct/', views3.direct_upload, name='direct_upload'),
    path('upload/estimate-price', views3.get_price, name='get_price'),
    path('upload/translate', views3.start_translate, name='start_translate'),
    path('upload/download/<str:task_id>/', views3.download_file, name='download_file'),
    path('upload/ajax-status/<str:task_id>/', views3.ajax_task_status, name='ajax_task_status'),
]