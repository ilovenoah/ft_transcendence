# myproject/urls.py
from django.contrib import admin
from django.urls import path
from main import views

from .views import signup
from django.contrib.auth import views as auth_views
from .views import profile

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('page1/', views.page1, name='page1'),
    path('page2/', views.page2, name='page2'),
    path('page3/', views.page3, name='page3'),
    path('ponggame/', views.ponggame, name='ponggame'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html', redirect_authenticated_user=True), name='login'),
    path('accounts/profile/', profile, name='profile'),
]


# urlpatterns = [
#     path('signup/', signup, name='signup'),
#     path('login/', auth_views.LoginView.as_view(template_name='login.html', redirect_authenticated_user=True, success_url='/home/'), name='login'),
#     path('accounts/profile/', profile, name='profile'),
# ]
