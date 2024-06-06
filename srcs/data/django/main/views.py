# from django.shortcuts import render, redirect
import os
import json
import logging
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth import logout
from django.shortcuts import render
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .forms import ImageForm
from .forms import UsernameForm, EmailForm, AvatarForm, PasswordChangeForm
from .forms import SignUpForm



logger = logging.getLogger(__name__)



def index(request):
    return render(request, 'index.html')


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
            elif page == 'uploadtest':
                response_data = {
                    'page':page,
                    'content':read_file('upload.html'),
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
                    'scriptfiles': '/static/js/sspong.js',
                }
            elif page == 'signup':
                form = SignUpForm(data=post_data)
                if form.is_valid():
                    user = form.save()
                    response_data = {
                        'page':page,
                        'content': 'Signup successful',
                        'title': 'Signup Success'
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
                    user = request.user
                    user.is_online = True
                    user.last_active = timezone.now()
                    user.save(update_fields=['is_online', 'last_active'])
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
                    
                    response_data = {
                        'page': page,
                        'content': render_to_string('profile.html', {'user': user}),
                        'title': 'Profile',
                    }
                else:
                    form = AuthenticationForm()
                    response_data = {
                        'page': page,
                        'content': render_to_string('login.html', {'form': form, 'request': request}),
                        'title': 'Login',
                    }
            elif page == 'logout':
                user = request.user
                if user.is_authenticated:
                    user.is_online = False
                    user.last_active = timezone.now()
                    user.save(update_fields=['last_active', 'is_online'])
                    logout(request)
                    response_data = {
                        'page': page,
                        'content': 'logged out',
                        'title': 'Logout'
                    }
                else:
                    response_data = {
                        'page': page,
                        'content': read_file('top.html'),
                        'title': 'トラセントップ'
                    }
            elif page == 'edit_profile':
                user = request.user
                if user.is_authenticated:
                    form_edit_username = UsernameForm(data=post_data, instance=user)
                    form_edit_email = EmailForm(data=post_data, instance=user)
                    form_edit_avatar = AvatarForm(data=post_data, files=request.FILES, instance=user)
                    form_change_password = PasswordChangeForm(data=post_data, instance=user)
                    response_data = {
                        'page': page,
                        'content':render_to_string('edit_username.html', context={'form_edit_username': form_edit_username, 'request': request}) +
                            render_to_string('edit_email.html', context={'form_edit_email': form_edit_email, 'request': request}) +
                            render_to_string('edit_avatar.html', context={'form_edit_avatar': form_edit_avatar, 'request': request}) +
                            render_to_string('change_password.html', context={'form_change_password': form_change_password, 'request': request}),
                        'title': 'Edit Profile'
                    }
                else:
                    form = AuthenticationForm()
                    response_data = {
                        'page': page,
                        'content': render_to_string('login.html', {'form': form, 'request': request}),
                        'title': 'Login',
                    }
            elif page == 'edit_username':
                user = request.user
                if user.is_authenticated:
                    form_edit_username = UsernameForm(data=post_data, instance=user)
                    form_edit_email = EmailForm(data=post_data, instance=user)
                    form_edit_avatar = AvatarForm(data=post_data, files=request.FILES, instance=user)
                    form_change_password = PasswordChangeForm(data=post_data, instance=user)
                    if form_edit_username.is_valid():
                        user = form_edit_username.save()
                        response_data = {
                        'page': page,
                        'content': 'Saved',
                        'title': 'Saved'
                    }
                    else:
                        response_data = {
                            'page': page,
                            'content':render_to_string('edit_username.html', context={'form_edit_username': form_edit_username, 'request': request}) +
                                render_to_string('edit_email.html', context={'form_edit_email': form_edit_email, 'request': request}) +
                                render_to_string('edit_avatar.html', context={'form_edit_avatar': form_edit_avatar, 'request': request}) +
                                render_to_string('change_password.html', context={'form_change_password': form_change_password, 'request': request}),
                            'title': 'Edit Profile'
                        }
                else:
                    form = AuthenticationForm()
                    response_data = {
                        'page': page,
                        'content': render_to_string('login.html', {'form': form, 'request': request}),
                        'title': 'Login',
                    }
            elif page == 'edit_email':
                user = request.user
                if user.is_authenticated:
                    form_edit_username = UsernameForm(data=post_data, instance=user)
                    form_edit_email = EmailForm(data=post_data, instance=user)
                    form_edit_avatar = AvatarForm(data=post_data, files=request.FILES, instance=user)
                    form_change_password = PasswordChangeForm(data=post_data, instance=user)
                    if form_edit_email.is_valid():
                        user = form_edit_email.save()
                        response_data = {
                        'page': page,
                        'content': 'Saved',
                        'title': 'Saved'
                    }
                    else:
                        response_data = {
                            'page': page,
                            'content':render_to_string('edit_username.html', context={'form_edit_username': form_edit_username, 'request': request}) +
                                render_to_string('edit_email.html', context={'form_edit_email': form_edit_email, 'request': request}) +
                                render_to_string('edit_avatar.html', context={'form_edit_avatar': form_edit_avatar, 'request': request}) +
                                render_to_string('change_password.html', context={'form_change_password': form_change_password, 'request': request}),
                            'title': 'Edit Profile'
                        }
                else:
                    form = AuthenticationForm()
                    response_data = {
                        'page': page,
                        'content': render_to_string('login.html', {'form': form, 'request': request}),
                        'title': 'Login',
                    }
            elif page == 'edit_avatar':
                user = request.user
                if user.is_authenticated:
                    form_edit_username = UsernameForm(data=post_data, instance=user)
                    form_edit_email = EmailForm(data=post_data, instance=user)
                    form_edit_avatar = AvatarForm(data=post_data,  instance=user)
                    form_change_password = PasswordChangeForm(data=post_data, instance=user)
                    if form_edit_avatar.is_valid():
                        user = form_edit_avatar.save()
                        response_data = {
                            'page': page,
                            'content': 'Saved',
                            'title': 'Saved'
                        }
                    else:
                        response_data = {
                            'page': page,
                            'content':render_to_string('edit_username.html', context={'form_edit_username': form_edit_username, 'request': request}) +
                                render_to_string('edit_email.html', context={'form_edit_email': form_edit_email, 'request': request}) +
                                render_to_string('edit_avatar.html', context={'form_edit_avatar': form_edit_avatar, 'request': request}) +
                                render_to_string('change_password.html', context={'form_change_password': form_change_password, 'request': request}),
                            'title': 'Edit Profile',
                        }
                else:
                    form = AuthenticationForm()
                    response_data = {
                        'page': page,
                        'content': render_to_string('login.html', {'form': form, 'request': request}),
                        'title': 'Login',
                    }
            elif page == 'change_password':
                user = request.user
                if user.is_authenticated:
                    form_edit_username = UsernameForm(data=post_data, instance=user)
                    form_edit_email = EmailForm(data=post_data, instance=user)
                    form_edit_avatar = AvatarForm(data=post_data, files=request.FILES, instance=user)
                    form_change_password = PasswordChangeForm(data=post_data, instance=user)
                    if form_change_password.is_valid():
                        user = form_change_password.save()
                        response_data = {
                            'page': page,
                            'content': 'Saved',
                            'title': 'Saved'
                        }
                        user.is_online = False
                        user.save(update_fields=['is_online'])
                    else:
                        response_data = {
                            'page': page,
                            'content':render_to_string('edit_username.html', context={'form_edit_username': form_edit_username, 'request': request}) +
                                render_to_string('edit_email.html', context={'form_edit_email': form_edit_email, 'request': request}) +
                                render_to_string('edit_avatar.html', context={'form_edit_avatar': form_edit_avatar, 'request': request}) +
                                render_to_string('change_password.html', context={'form_change_password': form_change_password, 'request': request}),
                            'title': 'Edit Profile'
                        }
                else:
                    form = AuthenticationForm()
                    response_data = {
                        'page': page,
                        'content': render_to_string('login.html', {'form': form, 'request': request}),
                        'title': 'Login',
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


@login_required
def heartbeat(request):
    user = request.user
    user.last_active = timezone.now()
    user.save(update_fields=['last_active'])
    return JsonResponse({'status': 'logged_in'})

def get_csrf_token(request):
    token = get_token(request)
    return JsonResponse({'csrfToken': token})

@csrf_exempt
def upload_image(request):
    if request.method == 'POST':
        try:
            #受信データの処理            
            form = ImageForm(request.POST, request.FILES)
            if form.is_valid():
                image_instance = form.save()
                response_data = {
                    'msgtagid':'result',
                    'imgtagid':'uploaded',
                    'message':'アップロードが成功しました\nこの画像を保存しますか',
                    'imgsrc':'media/' + image_instance.image.name,
                    'descimage':'アップロード画像',
                    'exec':'document.getElementById(\'id_avatar\').value = "' + image_instance.image.name + '"',
                }
                return JsonResponse(response_data)
            else:
                return JsonResponse({'error': 'Invalid form data'}, status=400)
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

