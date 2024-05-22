# myproject/urls.py
from django.contrib import admin
from django.urls import path
from main import views
from .views import process_post_data

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('process-post/', process_post_data, name='process_post_data'),
    path('page1/', views.page1, name='page1'),
    path('page2/', views.page2, name='page2'),
    path('page3/', views.page3, name='page3'),
    path('ponggame/', views.ponggame, name='ponggame'),
]

