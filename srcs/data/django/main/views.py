# from django.shortcuts import render, redirect
import os
import json
import logging
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.shortcuts import render
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string
from .forms import SignUpForm
from django.contrib.auth import logout

logger = logging.getLogger(__name__)

# from django.contrib.auth.decorators import login_required

# from django.urls import reverse_lazy
# from django.views.generic import TemplateView

# from .forms import CustomUserChangeForm

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

# def profile(request):
#     return render(request, 'profile.html', {'user': request.user})


def index(request):
    return render(request, 'index.html')

def get_csrf_token(request):
    token = get_token(request)
    return JsonResponse({'csrfToken': token})

def process_post_data(request):
    if request.method == 'POST':
        try:
            #受信データの処理
            post_data = json.loads(request.body)
            page = post_data.get('page')   
            title = post_data.get('title') 
            content = post_data.get('content') 

            #送信データの作成
            if page == 'top':
                response_data = {
                    'page':page,
                    'content':read_file('top.html'),
                    'title': 'トラセントップ',
                }
            elif page == 'test':
                response_data = {
                    'page':page,
                    'content': 'testページ',
                    'title': 'test',
                    # 生のjavascriptを埋め込みたいとき
                    'rawscripts': 'console.log("test");',
                }
            elif page == 'formtest':
                response_data = {
                    'page':page,
                    'content':read_file('formtest.html'),
                    'title': title,
                }    
            elif page == 'form1':
                response_data = {
                    'page':page,
                    'content': content,
                    'title': title,
                }    
            elif page == 'ponggame':
                response_data = {
                    'page':page,
                    'content':read_file('ponggame.html'),
                    'title': title,
                    # javascriptのファイルを指定するとき
                    'scriptfiles': '/static/js/game.js',
                }
            elif page == 'signup':
                form = SignUpForm(data=post_data)
                if form.is_valid():
                    user = form.save()
                    response_data = {
                        'page':page,
                        'content': read_file('top.html'),
                        'title': 'トラセントップ'
                    }       
                else:
                    response_data = {
                        'page':page,
                        'content':render_to_string('signup.html', context={'form': form, 'request': request}),
                        'title': 'signup',
                    }
            elif page == 'login':
                form = AuthenticationForm(data=post_data)
                if form.is_valid():
                    login(request, form.get_user())
                    response_data = {
                        'page': page,
                        'content': 'Login successful',
                        'title': 'Login Success'
                    }
                else:
                    response_data = {
                        'page': page,
                        'content': render_to_string('login.html', {'form': form, 'request': request}),
                        'title': 'Login'
                    }
            elif page == 'profile':
                user = request.user
                if user.is_authenticated:
                    context = {'user': user}
                    response_data = {
                        'page': page,
                        'content': render_to_string('profile.html', context),
                        'title': 'Profile',
                    }
                else:
                    form = AuthenticationForm()  # ログインフォームのインスタンスを作成
                    response_data = {
                        'page': page,
                        'content': render_to_string('login.html', {'form': form, 'request': request}),
                        'title': 'Login',
                    }
            elif page == 'logout':
                logout(request)
                response_data = {
                    'page': page,
                    'content': read_file('top.html'),
                    'title': 'トラセントップ'
                }
            else:
                if is_file_exists(page + '.html') :
                    response_data = {
                        'page':page,
                        # contentにmain/htmlの下のファイルを指定するとき
                        'content':read_file(page + '.html'),
                        'title': title,
                    }
                else: #指定のファイルが main/htmlの下に存在しないとき
                    response_data = {
                        'page':page,
                        'content':read_file('default.html'),
                        'title': '42-ft_transcendence',
                    }
            return JsonResponse(response_data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

#ファイルの存在チェック
def is_file_exists(filename):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # ファイルのパスを構築
    file_path = os.path.join(base_dir, 'main/html', filename)
    if not os.path.exists(file_path):
        #raise FileNotFoundError(f"The file '{filepath}' does not exist.")
        return False
    return True

# class CustomLogoutView(TemplateView):
#     template_name = 'logout.html'

#     def post(self, request, *args, **kwargs):
#         logout(request)
#         return redirect(self.get_success_url())
    
#     def get_success_url(self):
#         return reverse_lazy('index')  # ログアウト後のリダイレクト先

# @login_required
# def edit_profile(request):
#     if request.method == 'POST':
#         form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
#         if form.is_valid():
#             form.save()
#             return redirect('index')  
#     else:
#         form = CustomUserChangeForm(instance=request.user)
#     return render(request, 'edit_profile.html', {'form': form})

#ファイルの中身を返す
def read_file(filename):
    # プロジェクトのベースディレクトリを取得
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # ファイルのパスを構築
    file_path = os.path.join(base_dir, 'main/html', filename)
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return "Error: File not found."
    except Exception as e:
        return f"Error: {e}"