from django.shortcuts import render, redirect
from .forms import SignUpForm
from django.contrib.auth.decorators import login_required

from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth import logout

from .forms import CustomUserChangeForm

def index(request):
    return render(request, 'index.html')
def page1(request):
    return render(request, 'page1.html')
def page2(request):
    return render(request, 'page2.html')
def page3(request):
    return render(request, 'page3.html')
def ponggame(request):
    return render(request, 'ponggame.html')

def profile(request):
    return render(request, 'profile.html', {'user': request.user})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # 任意: ユーザーをログインさせる
            # from django.contrib.auth import authenticate, login
            # username = form.cleaned_data.get('username')
            # raw_password = form.cleaned_data.get('password1')
            # user = authenticate(username=username, password=raw_password)
            # login(request, user)
            return redirect('index')  # 登録後にリダイレクトするページ
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

class CustomLogoutView(TemplateView):
    template_name = 'logout.html'

    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect(self.get_success_url())
    
    def get_success_url(self):
        return reverse_lazy('index')  # ログアウト後のリダイレクト先

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('index')  
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(request, 'edit_profile.html', {'form': form})

