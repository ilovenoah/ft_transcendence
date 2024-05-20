# from django.shortcuts import render

# def index(request):
#     return render(request, 'index.html')
# def page1(request):
#     return render(request, 'page1.html')
# def page2(request):
#     return render(request, 'page2.html')
# def page3(request):
#     return render(request, 'page3.html')
# def ponggame(request):
#     return render(request, 'ponggame.html')

from django.shortcuts import render, redirect
from .forms import SignUpForm
from django.contrib.auth.decorators import login_required

def profile(request):
    return render(request, 'profile.html', {'user': request.user})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            # 任意: ユーザーをログインさせる
            # from django.contrib.auth import authenticate, login
            # username = form.cleaned_data.get('username')
            # raw_password = form.cleaned_data.get('password1')
            # user = authenticate(username=username, password=raw_password)
            # login(request, user)
            return redirect('login')  # 登録後にリダイレクトするページ
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})




