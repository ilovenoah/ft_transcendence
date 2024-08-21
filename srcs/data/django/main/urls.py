# myproject/urls.py
from django.contrib import admin
from django.urls import path, include
from main import views
from django.conf import settings
from django.conf.urls.static import static
from .views import process_post_data
from .views import upload_image
from .views import heartbeat

urlpatterns = [
    path('', views.index, name='index'),
    path('process-post/', process_post_data, name='process_post_data'),
    path('get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),
    path('upload/', upload_image, name='upload_image'),    
    path('heartbeat/', heartbeat, name='heartbeat'),
    path('gameHeartbeat/<str:roomid>/', views.gameHeartbeat, name='gameHeartbeat'),
    path('getLanguage/<str:lang>/', views.getLanguage, name='getLanguage'),
    path('setLanguage/<str:lang>/', views.setLanguage, name='setLanguage'),
    path('i18n/', include('django.conf.urls.i18n')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
