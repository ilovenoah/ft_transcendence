# from django.shortcuts import render, redirect
import os
import json
import logging
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
from .forms import SignUpForm, EmailForm, AvatarForm, DisplayNameForm, PasswordChangeForm, ImageForm, FriendRequestForm, FriendRequestForm
from .models import CustomUser, FriendRequest, Matchmaking, Tournament, TournamentUser
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db import models

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
                    'scriptfiles': '/static/js/game.js',
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
                    if user.is_first == True:
                        user.is_first = False
                        user.save(update_fields=['is_first'])
                        form_edit_display_name = DisplayNameForm(data=post_data, instance=user)
                        response_data = {
                            'page': page,
                            'content':render_to_string('edit_display_name.html', context={'form_edit_display_name': form_edit_display_name, 'request': request}),
                            'title': 'Edit Display Name'
                        }
                    else:
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
                    form_edit_email = EmailForm(data=post_data, instance=user)
                    form_edit_display_name = DisplayNameForm(data=post_data, instance=user)
                    form_edit_avatar = AvatarForm(data=post_data, files=request.FILES, instance=user)
                    form_change_password = PasswordChangeForm(data=post_data, instance=user)
                    response_data = {
                        'page': page,
                        'content': render_to_string('edit_email.html', context={'form_edit_email': form_edit_email, 'request': request}) +
                            render_to_string('edit_display_name.html', context={'form_edit_display_name': form_edit_display_name, 'request': request}) +
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
                    form_edit_email = EmailForm(data=post_data, instance=user)
                    form_edit_display_name = DisplayNameForm(data=post_data, instance=user)
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
                            'content': render_to_string('edit_email.html', context={'form_edit_email': form_edit_email, 'request': request}) +
                                render_to_string('edit_display_name.html', context={'form_edit_display_name': form_edit_display_name, 'request': request}) +
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
            elif page == 'edit_display_name':
                user = request.user
                if user.is_authenticated:
                    form_edit_email = EmailForm(data=post_data, instance=user)
                    form_edit_display_name = DisplayNameForm(data=post_data, instance=user)
                    form_edit_avatar = AvatarForm(data=post_data, files=request.FILES, instance=user)
                    form_change_password = PasswordChangeForm(data=post_data, instance=user)
                    if form_edit_display_name.is_valid():
                        user = form_edit_display_name.save()
                        response_data = {
                        'page': page,
                        'content': 'Saved',
                        'title': 'Saved'
                    }
                    else:
                        response_data = {
                            'page': page,
                            'content': render_to_string('edit_email.html', context={'form_edit_email': form_edit_email, 'request': request}) +
                                render_to_string('edit_display_name.html', context={'form_edit_display_name': form_edit_display_name, 'request': request}) +
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
                    form_edit_email = EmailForm(data=post_data, instance=user)
                    form_edit_display_name = DisplayNameForm(data=post_data, instance=user)
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
                            'content': render_to_string('edit_email.html', context={'form_edit_email': form_edit_email, 'request': request}) +
                                render_to_string('edit_display_name.html', context={'form_edit_display_name': form_edit_display_name, 'request': request}) +
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
                    form_edit_email = EmailForm(data=post_data, instance=user)
                    form_edit_display_name = DisplayNameForm(data=post_data, instance=user)
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
                            'content': render_to_string('edit_email.html', context={'form_edit_email': form_edit_email, 'request': request}) +
                                render_to_string('edit_display_name.html', context={'form_edit_display_name': form_edit_display_name, 'request': request}) +
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
            elif page == 'friend_request':
                user = request.user
                if user.is_authenticated:
                    form = FriendRequestForm(data=post_data, from_user=request.user)
                    if form.is_valid():
                        to_user = form.cleaned_data['to_user']
                        try:
                            response_data = {
                                    'page': page,
                                    'content': 'Friend Request Sent',
                                    'title': 'Friend Request Sent'
                                }
                            request.user.send_friend_request(to_user)
                        except ValidationError as e:
                            form.add_error(None, e)  # エラーをフォームに追加
                            response_data = {
                                'page': page,
                                'content': render_to_string('friend_request.html', {'form': form, 'request': request}),
                                'title': 'Friend Request',
                            }
                    else:
                        response_data = {
                            'page': page,
                            'content': render_to_string('friend_request.html', {'form': form, 'request': request}),
                            'title': 'Friend Request',
                        }  
                else:
                    form = AuthenticationForm()
                    response_data = {
                        'page': page,
                        'content': render_to_string('login.html', {'form': form, 'request': request}),
                        'title': 'Login',
                    }
            elif page == 'friend_request_list':
                user = request.user
                if user.is_authenticated:
                    form = FriendRequestActionForm(data=post_data, prefix=post_data.get('prefix'))
                    if form.is_valid():
                        action = form.cleaned_data['action']
                        request_id = post_data.get('request_id')
                        friend_request = get_object_or_404(FriendRequest, id=request_id)
                        if action == 'accept':
                            friend_request.accept_request()
                        elif action == 'decline':
                            friend_request.decline_request()
                        response_data = {
                            'page': page,
                            'content': 'Sent',
                            'title': 'Sent',
                        }
                    else:
                        friend_requests = FriendRequest.objects.filter(to_user=request.user, status='P')
                        forms = {fr.id: (fr, FriendRequestActionForm(prefix=str(fr.id))) for fr in friend_requests}
                        response_data = {
                            'page': page,
                            'content': render_to_string('friend_request_list.html', {
                                'form': form, 
                                'request': request, 
                                'fr': friend_requests,
                                'forms': forms,
                            }),
                            'title': 'Friend Request List',
                        }
                else:
                    form = AuthenticationForm()
                    response_data = {
                        'page': page,
                        'content': render_to_string('login.html', {'form': form, 'request': request}),
                        'title': 'Login',
                    }
            elif page == 'friends':
                user = request.user
                if user.is_authenticated:
                    friends = CustomUser.objects.filter(
                        Q(friend_requests_sent__to_user=user, friend_requests_sent__status='A') |
                        Q(friend_requests_received__from_user=user, friend_requests_received__status='A')
                    ).distinct()
                    # 現在時刻から5分前の時刻を計算
                    five_minutes_ago = timezone.now() - timedelta(minutes=5)
                    # 各友達のオンラインステータスを設定
                    for friend in friends:
                        if friend.is_online and friend.last_active >= five_minutes_ago:
                            friend.online_status = 'Online'
                        else:
                            friend.online_status = 'Offline'
                    response_data = {
                        'page': page,
                        'content': render_to_string('friends.html', {'friends': friends}),
                        'title': 'Login',
                    }
                else:
                    form = AuthenticationForm()
                    response_data = {
                        'page': page,
                        'content': render_to_string('login.html', {'form': form, 'request': request}),
                        'title': 'Login',
                    }
            elif page == 'lobby':
                user = request.user
                if user.is_authenticated:
                    rooms = get_available_rooms()
                    tournaments = get_available_tournaments()
                    response_data = {
                        'page': page,
                        'content': render_to_string('lobby.html', {'rooms': rooms, 'tournaments': tournaments}),
                        'title': 'Lobby'
                    }
                else:
                    form = AuthenticationForm()
                    response_data = {
                        'page': page,
                        'content': render_to_string('login.html', {'form': form, 'request': request}),
                        'title': 'Login',
                    }
            elif page == 'enter_room':
                room_id = post_data.get('room_id')
                room = Matchmaking.objects.filter(id=room_id, user2__isnull=True).first()
                if room:
                    room.user2 = request.user
                    room.save()
                    response_data = {
                        'page':page,
                        'content':read_file('ponggame.html'),
                        'title': title,
                        'scriptfiles': '/static/js/game.js',
                    }
                else:
                    rooms = get_available_rooms()
                    tournaments = get_available_tournaments()
                    response_data = {
                        'page': page,
                        'content': render_to_string('lobby.html', {'rooms': rooms, 'tournaments': tournaments}),
                        'title': 'Lobby',
                    }
            elif page == 'create_room':
                user = request.user
                if user.is_authenticated:
                    current_user = user
                    current_time = timezone.now()
                    existing_match = Matchmaking.objects.filter(user1=current_user, timestamp__gte=current_time - timezone.timedelta(seconds=30)).first()
                    if existing_match and existing_match.user2: #user1とuser2が存在していてtimestampから30秒以内=マッチ->ゲームに移動
                        response_data = {
                            'page':page,
                            'content':read_file('ponggame.html'),
                            'title': title,
                            'scriptfiles': '/static/js/game.js',
                        }
                        return JsonResponse(response_data)   
                    existing_match = Matchmaking.objects.filter(user1=current_user, timestamp__gte=current_time - timezone.timedelta(seconds=30)).first()
                    if existing_match: #current_userがuser1と同じ->timestampを更新
                        existing_match.timestamp = current_time
                        existing_match.save()
                    else: #user1が存在しない->ルームを作成
                        Matchmaking.objects.create(user1=current_user)
                    response_data = {
                        'page': page,
                        'content': read_file('room.html'),
                        'title': 'Room',
                        'reload': page,
                        'timeout' : '10000',
                        'alert': 'Please, wait a moment.',
                   }
                else:
                    form = AuthenticationForm()
                    response_data = {
                        'page': page,
                        'content': render_to_string('login.html', {'form': form, 'request': request}),
                        'title': 'Login',
                    }
            elif page == 'create_tournament':
                user = request.user
                if user.is_authenticated:
                    size = post_data.get('size')
                    tournament = Tournament.objects.create(size=size, count=1)
                    TournamentUser.objects.create(tournament=tournament, user=user)
                    page = 'tournament'
                    response_data = {
                        'page': page,
                        'content': read_file('tournament.html'),
                        'title': 'tournament',
                        'reload': page,
                        'timeout' : '10000',
                        'alert': 'Please, wait a moment.',
                    }
                else:
                    form = AuthenticationForm()
                    response_data = {
                        'page': page,
                        'content': render_to_string('login.html', {'form': form, 'request': request}),
                        'title': 'Login',
                    }
            elif page == 'tournament':
                user = request.user
                thirty_seconds_ago = timezone.now() - timezone.timedelta(seconds=30)
                tournament_user = TournamentUser.objects.filter(user=user, is_complete=False, timestamp__gte=thirty_seconds_ago).first()
                tournament_user.timestamp = timezone.now()
                tournament_user.save()
                tournament = tournament_user.tournament
                count = TournamentUser.objects.filter(tournament=tournament, timestamp__gte=thirty_seconds_ago).count() #トーナメントが同じでtimestampが30秒以内のuserの数
                tournament.count = count
                tournament.save()
                if count == tournament.size:
                    tournament_user.is_complete = True
                    tournament_user.save()
                    room = Matchmaking.objects.filter(user2__isnull=True, timestamp__gte=thirty_seconds_ago, tournament=tournament).first()
                    if room: #tournamentが同じでuser2が不在でtimestampから30秒以内のroom
                        room.user2 = user
                        room.save()
                    else:
                        Matchmaking.objects.create(user1=user, tournament=tournament)
                    response_data = {
                        'page':page,
                        'content':read_file('ponggame.html'),
                        'title': title,
                        'scriptfiles': '/static/js/game.js',
                    }
                else:
                    response_data = {
                        'page': page,
                        'content': read_file('tournament.html'),
                        'title': 'tournament',
                        'reload': page,
                        'timeout' : '10000',
                        'alert': 'Please, wait a moment.',
                    }
            elif page == 'join_tournament':
                user = request.user
                tournament_id = post_data.get('tournament_id')
                tournament = Tournament.objects.filter(id=tournament_id).first()
                tournament_user = TournamentUser.objects.create(tournament=tournament, user=user)
                thirty_seconds_ago = timezone.now() - timezone.timedelta(seconds=30)
                count = TournamentUser.objects.filter(tournament=tournament, timestamp__gte=thirty_seconds_ago).count()
                tournament.count = count 
                tournament.save()
                if count == tournament.size:
                    tournament_user.is_complete = True
                    tournament_user.save()
                    room = Matchmaking.objects.filter(user2__isnull=True, timestamp__gte=thirty_seconds_ago, tournament=tournament).first()
                    if room: #tournamentが同じでuser2が不在でtimestampから30秒以内のroom
                        room.user2 = user
                        room.save()
                    else:
                        Matchmaking.objects.create(user1=user, tournament=tournament)
                    response_data = {
                        'page':page,
                        'content':read_file('ponggame.html'),
                        'title': title,
                        'scriptfiles': '/static/js/game.js',
                    }
                else:
                    page = 'tournament'
                    response_data = {
                        'page': page,
                        'content': read_file('tournament.html'),
                        'title': 'tournament',
                        'reload': page,
                        'timeout' : '10000',
                        'alert': 'Please, wait a moment.',
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
                    'setid': 'id_avatar',
                    'setvalue': image_instance.image.name,
#                    'exec':'document.getElementById(\'id_avatar\').value = "' + image_instance.image.name + '"',
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


@login_required
def heartbeat(request):
    user = request.user
    user.last_active = timezone.now()
    user.save(update_fields=['last_active'])
    return JsonResponse({'status': 'logged_in'})

#user2が不在でtimestampから30秒以内のroomを取得
def get_available_rooms():
    current_time = timezone.now()
    thirty_seconds_ago = current_time - timedelta(seconds=30)
    available_rooms = Matchmaking.objects.filter(
        user2__isnull=True,
        timestamp__gte=thirty_seconds_ago
    )
    return available_rooms

#countがsizeより小さくtimestampから30秒以内のtournamentを取得
def get_available_tournaments():
    current_time = timezone.now()
    thirty_seconds_ago = current_time - timedelta(seconds=30)
    available_tournaments = Tournament.objects.filter(
        count__lt=models.F('size'), 
        timestamp__gte=thirty_seconds_ago
    )
    return available_tournaments
