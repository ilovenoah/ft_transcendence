# myproject/urls.py
from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('first/', views.first, name='first'),
    path('second/', views.second, name='second'),
]