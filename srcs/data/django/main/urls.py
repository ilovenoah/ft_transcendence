# myproject/urls.py
from django.contrib import admin
from django.urls import path
from main import views
from .views import process_post_data

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('process-post/', process_post_data, name='process_post_data'),
    path('ponggame/', views.ponggame, name='ponggame'),
]

