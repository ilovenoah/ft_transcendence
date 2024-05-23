# myproject/urls.py
from django.contrib import admin
from django.urls import path
from main import views
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.auth import views as auth_views

from .views import CustomLogoutView  # カスタムビューをインポート

from .views import edit_profile

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('page1/', views.page1, name='page1'),
    path('page2/', views.page2, name='page2'),
    path('page3/', views.page3, name='page3'),
    path('ponggame/', views.ponggame, name='ponggame'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/profile/', views.profile, name='profile'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
