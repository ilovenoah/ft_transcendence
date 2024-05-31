# myproject/urls.py
from django.contrib import admin
from django.urls import path, include
from main import views
from django.conf import settings
from django.conf.urls.static import static
from .views import process_post_data

urlpatterns = [
    path('', views.index, name='index'),
    path('process-post/', process_post_data, name='process_post_data'),
    path('get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
