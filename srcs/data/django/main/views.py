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
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
from .forms import SignUpForm, EmailForm, AvatarForm, DisplayNameForm, PasswordChangeForm, ImageForm, FriendRequestForm, FriendRequestActionForm, LoginForm
from .forms import CustomizeGameForm, CustomizeSinglePlayForm, CustomizeTournamentForm, CustomizeDoublesForm
from .models import CustomUser, FriendRequest, Matchmaking, Tournament, TournamentUser, Doubles, DoublesUser
from django.core.exceptions import ValidationError
from django.db.models import Q, F, ExpressionWrapper, IntegerField
from django.db import models
from math import log2, ceil
from PIL import Image as PilImage, Image
from django.core.files.base import ContentFile
from io import BytesIO

logger = logging.getLogger(__name__)


def index(request):
    return render(request, 'index.html', context={})

def process_post_data(request):
    if request.method == 'POST':
        try:
            #受信データの処理
            post_data = json.loads(request.body)
            page = post_data.get('page')   
            title = post_data.get('title') 
            content = post_data.get('content') 
            gameid = post_data.get('gameid') 
            # loginlang = post_data.get('lang') 

            #送信データの作成
            if page == 'logout':
                user = request.user
                if user.is_authenticated:
                    user.is_online = False
                    user.last_active = timezone.now() - timedelta(minutes=5)
                    user.save(update_fields=['is_online', 'last_active'])
                    logout(request)
                    response_data = {
                        'page': 'login',
                        'content': read_file('top.html'),
                        'title': 'Login',
                        'login': 'false',
                        'elem': 'top',
                        'alert': 'ログアウトしました'
                    }
                else:
                    response_data = {
                        'page': page,
                        'content': read_file('top.html'),
                        'title': 'トラセントップ',
                        'login': 'true',
                        'elem': 'top',
                        'username' : user.username,
                    }
                return JsonResponse(response_data)
            user = request.user
            if user.is_authenticated:
                if not user.display_name:
                    form_edit_display_name = DisplayNameForm(data=post_data, instance=user)
                    if form_edit_display_name.is_valid():
                        user = form_edit_display_name.save()
                        response_data = {
                            'page': 'top',
                            'content': read_file('top.html'),
                            'title': 'トラセントップ',
                            'login': 'true',
                            'username' : user.username,
                            'elem': 'top'
                        }  
                    else:
                        response_data = {
                            'page': page,
                            'content':render_to_string('edit_display_name.html', context={'form_edit_display_name': form_edit_display_name, 'request': request}),
                            'title': 'Edit Display Name',
                            'login': 'true',
                            'username' : user.username,
                        }
                    return JsonResponse(response_data)
            if page == 'top':
                user = request.user
                if user.is_authenticated:
                    response_data = {
                        'page':page,
                        'content':read_file('top.html'),
                        'title': 'トラセントップ',
                        'username' : user.username,
                        'login': 'true',
                        'elem': 'top'
                    }
                else:
                    response_data = {
                        'page':page,
                        'content':read_file('top.html'),
                        'title': 'トラセントップ',
                        'login': 'false',
                        'elem': 'top'
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
            # elif page == 'ponggame':
            #     response_data = {
            #         'page':page,
            #         'content':read_file('ponggame.html'),
            #         'title': title,
            #         'gameid': gameid, 
            #         # javascriptのファイルを指定するとき
            #         'scriptfiles': '/static/js/sspong.js?gameid=' + gameid,
            #     }
            # elif page == 'ponggame2':
            #     response_data = {
            #         'page':page,
            #         'content':read_file('ponggame.html'),
            #         'title': title,
            #         'gameid': gameid, 
            #         # 生のjavascriptを埋め込みたいとき
            #         'rawscripts': 'startGame(' + gameid + '42,' +  str(request.user.id) + ')',
            #     }
            elif page == 'gamelist':
                response_data = {
                    'page':page,
                    'content':read_file('gamelist.html'),
                    'title': title,
                }
            elif page == 'signup':
                form = SignUpForm(data=post_data)
                if form.is_valid():
                    user = form.save()
                    form = LoginForm(data=post_data)
                    response_data = {
                        'page': 'login',
                        'content': render_to_string('login.html', {'form': form, 'request': request}),
                        'title': 'Login',
                        'alert': 'サインアップしました',
                        'test': 'test'
                    }       
                else:
                    response_data = {
                        'page':page,
                        'content':render_to_string('signup.html', context={'form': form, 'request': request}),
                        'title': 'signup'
                    }
            elif page == 'login':
                form = LoginForm(data=post_data)
                if form.is_valid():
                    login(request, form.get_user())
                    user = request.user
                    user.is_online = True
                    user.last_active = timezone.now()
                    
                    lang = user.language
                    if lang == "":
                        lang = post_data.get('lang') 
                        user.language = lang
                        user.save(update_fields=['language'])
                    user.save(update_fields=['is_online', 'last_active'])

                    if not user.display_name:
                        form_edit_display_name = DisplayNameForm(data=post_data, instance=user)
                        if form_edit_display_name.is_valid():
                            user = form_edit_display_name.save()
                            response_data = {
                                'page': 'top',
                                'content': read_file('top.html'),
                                'title': 'トラセントップ',
                                'login': 'true',
                                'username' : user.username,
                                'elem': 'top',
                                'lang': lang,
                            }  
                        else:
                            response_data = {
                                'page': 'display_name_form',
                                'content':render_to_string('edit_display_name.html', context={'form_edit_display_name': form_edit_display_name, 'request': request}),
                                'title': 'Edit Display Name',
                                'login': 'true',
                                'username' : user.username,
                                'lang': lang
                            }
                        return JsonResponse(response_data)
                    response_data = {
                        'page': 'top',
                        'content': read_file('top.html'),
                        'title': 'トラセントップ',
                        'login': 'true',
                        'username' : user.username,
                        'elem': 'top', 
                        'alert': 'ログインしました',
                        'lang': lang
                    }   
                else:
                    response_data = {
                        'page': page,
                        'content': render_to_string('login.html', {'form': form, 'request': request}),
                        'title': 'Login',
                        'login': 'false',
                        'elem': 'login',
                        'rawscripts': 'embedLoginLang();',
                    }
            elif page == 'profile':
                user = request.user
                if user.is_authenticated:
                    win = Matchmaking.objects.filter(winner=user).count()
                    loss = calculate_loss(user, win)
                    if win + loss == 0:
                        win_rate = 0
                    else:
                        win_rate = int(win * 100 / (win + loss))
                    response_data = {
                        'page': page,
                        'content': render_to_string('profile.html', {'user': user, 'win_rate': win_rate, 'win': win, 'loss': loss}),
                        'title': 'Profile',
                    }
                else:
                    form = LoginForm(data=post_data)
                    response_data = {
                        'page': page,
                        'content': render_to_string('login.html', {'form': form, 'request': request}),
                        'title': 'Login',
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
                    form = LoginForm(data=post_data)
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
                            'page': 'profile',
                            'content': render_to_string('profile.html', {'user': user}),
                            'title': 'Profile',
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
                    form = LoginForm(data=post_data)
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
                            'page': 'profile',
                            'content': render_to_string('profile.html', {'user': user}),
                            'title': 'Profile',
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
                    form = LoginForm(data=post_data)
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
                            'page': 'profile',
                            'content': render_to_string('profile.html', {'user': user}),
                            'title': 'Profile',
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
                    form = LoginForm(data=post_data)
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
                        user.is_online = False
                        user.save(update_fields=['is_online'])
                        response_data = {
                            'page': 'login',
                            'content': read_file('top.html'),
                            'title': 'Login',
                            'login': 'false'
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
                    form = LoginForm(data=post_data)
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
                            request.user.send_friend_request(to_user)
                            friend_requests = FriendRequest.objects.filter(to_user=request.user, status='P')
                            forms = {fr.id: (fr, FriendRequestActionForm(prefix=str(fr.id))) for fr in friend_requests}
                            response_data = {
                                'page': page,
                                'content': render_to_string('friend_request.html', {'form': form, 'request': request}) +
                                    render_to_string('friend_request_list.html', {'forms': forms,}),
                                'title': 'Friend Request',
                                'alert': '追加しました',
                            }
                        except Exception as e:
                            friend_requests = FriendRequest.objects.filter(to_user=request.user, status='P')
                            forms = {fr.id: (fr, FriendRequestActionForm(prefix=str(fr.id))) for fr in friend_requests}
                            response_data = {
                                'page': page,
                                'content': render_to_string('friend_request.html', {'form': form, 'request': request}) +
                                    render_to_string('friend_request_list.html', {'forms': forms,}),
                                'title': 'Friend Request',
                            }
                    else:
                        friend_requests = FriendRequest.objects.filter(to_user=request.user, status='P')
                        forms = {fr.id: (fr, FriendRequestActionForm(prefix=str(fr.id))) for fr in friend_requests}
                        response_data = {
                            'page': page,
                            'content': render_to_string('friend_request.html', {'form': form, 'request': request}) +
                                render_to_string('friend_request_list.html', {'forms': forms,}),
                            'title': 'Friend Request',
                        }  
                else:
                    form = LoginForm(data=post_data)
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
                    friend_requests = FriendRequest.objects.filter(to_user=request.user, status='P')
                    forms = {fr.id: (fr, FriendRequestActionForm(prefix=str(fr.id))) for fr in friend_requests}
                    form = FriendRequestForm(data=post_data, from_user=request.user) 
                    response_data = {
                        'page': page,
                        'content': render_to_string('friend_request.html', {'form': form, 'request': request}) +
                            render_to_string('friend_request_list.html', {'forms': forms,}),
                        'title': 'Friend Request List',
                        'alert': '承認しました'
                    }
                else:
                    form = LoginForm(data=post_data)
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
                        if friend.last_active >= five_minutes_ago:
                            friend.is_online = True
                        else:
                            friend.is_online = False
                        friend.save()
                    pending_requests = FriendRequest.objects.filter(from_user_id=user.id, status='P')
                    response_data = {
                        'page': page,
                        'content': render_to_string('friends.html', {'friends': friends}) +
                            render_to_string('pending.html', {'pending_requests': pending_requests, 'request': request}),
                        'title': 'Friends',
                    }
                else:
                    form = LoginForm(data=post_data)
                    response_data = {
                        'page': page,
                        'content': render_to_string('login.html', {'form': form, 'request': request}),
                        'title': 'Login',
                    }
            elif page == 'lobby':
                user = request.user
                if user.is_authenticated:
                    rooms = get_available_rooms(user)
                    tournaments = get_available_tournaments(user)
                    final_matches = get_final_matches(user)
                    doubles = get_available_doubles(user)
                    response_data = {
                        'page': page,
                        'content': render_to_string('lobby.html', {'rooms': rooms, 'tournaments': tournaments, 'final_matches': final_matches, 'doubles': doubles}),
                        'title': 'Lobby'
                    }
                else:
                    form = LoginForm(data=post_data)
                    response_data = {
                        'page': page,
                        'content': render_to_string('login.html', {'form': form, 'request': request}),
                        'title': 'Login',
                    }
            elif page == 'enter_room':
                user = request.user
                room_id = post_data.get('room_id')
                room = Matchmaking.objects.filter(id=room_id, timestamp__gte=timezone.now() - timezone.timedelta(seconds=30)).first()
                if room:
                    if room.user2: #user2が存在している→再入室　
                        room.timestamp = timezone.now()
                        room.save()
                        gameplayer = 1
                        if room.user2 == user:
                            gameplayer = 2
                        response_data = {
                                'page':page,
                                'content':render_to_string('ponggame.html', {'room': room}),
                                'title': 'Pong Game ' + str(room.id),
                                # 生のjavascriptを埋め込みたいとき
                                'rawscripts': 'startGame(' + str(room.id) + ', ' + str(gameplayer) + ', ' +  str(request.user.id) + ', 0, ' + str(room.paddle_size) + ', \'' + str(room.is_3d) + '\', 0, 1)', 
                            }
                    else: #user2が存在していない 
                        if room.user1 == user: #user1とuser2が同一
                            room.timestamp = timezone.now()
                            room.save()
                            response_data = {
                                'page': page,
                                'content': read_file('waiting.html'),
                                'title': 'Room',
                                'reload': page,
                                'timeout' : '10000',
                                'alert': '対戦相手を待っています',
                        }
                        else: #user2として入室
                            room.user2 = user
                            room.save()
                            response_data = {
                                'page':page,
                                'content':render_to_string('ponggame.html', {'room': room}),
                                'title': 'Pong Game ' + str(room.id),
                                'gameid': str(room.id), 
                                # 生のjavascriptを埋め込みたいとき
                                'rawscripts': 'startGame(' + str(room.id) + ', 2, ' +  str(user.id) + ', 0, ' + str(room.paddle_size) + ', \'' + str(room.is_3d) + '\', 0, 0)', 
                            }
                else:
                    rooms = get_available_rooms(user)
                    tournaments = get_available_tournaments(user)
                    doubles = get_available_doubles(user)
                    final_matches = get_final_matches(user)
                    response_data = {
                        'page': page,
                        'content': render_to_string('lobby.html', {'rooms': rooms, 'tournaments': tournaments, 'final_matches': final_matches, 'doubles': doubles}),
                        'title': 'Lobby'
                    }
            elif page == 'create_room':
                user = request.user   
                if user.is_authenticated:
                    form = CustomizeGameForm(data=post_data)
                    if form.is_valid():
                        ball_speed = form.cleaned_data['ball_speed']
                        paddle_size = form.cleaned_data['paddle_size']
                        match_point = form.cleaned_data['match_point']
                        is_3d = form.cleaned_data['is_3d']
                        room = Matchmaking.objects.create(user1=user, ball_speed=ball_speed, paddle_size=paddle_size, match_point=match_point, is_3d=is_3d)
                        request.session['room_id'] = room.id
                        page = 'room'
                        response_data = {
                            'page': page,
                            'content': read_file('waiting.html'),
                            'title': 'Room',
                            'reload': page,
                            'timeout' : '10000',
                            'alert': '対戦相手を待っています',
                        }
                    else:
                        response_data = {
                            'page': page,
                            'content': render_to_string('customize_game.html', {'form': form}),
                            'title': 'customize game'
                        }
                else:
                    form = LoginForm(data=post_data)
                    response_data = {
                        'page': page,
                        'content': render_to_string('login.html', {'form': form, 'request': request}),
                        'title': 'Login',          
                    }
            elif page == 'room':
                user = request.user
                room_id = request.session.get('room_id')
                room = Matchmaking.objects.get(id=room_id)
                # room = Matchmaking.objects.filter(timestamp__gte=timezone.now() - timezone.timedelta(seconds=30), id=room_id).first()
                if room: 
                    if not room.user2:
                        room.timestamp = timezone.now()
                        room.save()
                        response_data = {
                            'page': page,
                            # 'content': read_file('room.html'),
                            # 'title': 'Pong Game ' + str(room.id),
                            'content': read_file('waiting.html'),
                            'title': 'Room',
                            'reload': page,
                            'timeout' : '10000',
                            'alert': '対戦相手を待っています',
                        }
                    else: #待ってるからplayer1として入室
                        response_data = {
                            # 'page':page,
                            # 'content':read_file('ponggame.html'),
                            # 'title': title,
                            # 'scriptfiles': '/static/js/game.js',
                            'page':page,
                            'content':render_to_string('ponggame.html', {'room': room}),
                            'title': 'Pong Game ' + str(room.id),
                            'gameid': str(room.id), 
                            # 生のjavascriptを埋め込みたいとき
                            'rawscripts': 'startGame(' + str(room.id) + ', 1,' +  str(request.user.id) + ', 0, ' + str(room.paddle_size) + ', \'' + str(room.is_3d) + '\', 0, 0)', 
                        }
                else:
                    rooms = get_available_rooms(user)
                    tournaments = get_available_tournaments(user)
                    doubles = get_available_doubles(user)
                    final_matches = get_final_matches(user)
                    response_data = {
                        'page': page,
                        'content': render_to_string('lobby.html', {'rooms': rooms, 'tournaments': tournaments, 'final_matches': final_matches, 'doubles': doubles}),
                        'title': 'Lobby'
                    }
            elif page == 'create_tournament':
                user = request.user
                if user.is_authenticated:
                    size = post_data.get('size')
                    form = CustomizeTournamentForm(data=post_data)
                    if form.is_valid():
                        ball_speed = form.cleaned_data['ball_speed']
                        paddle_size = form.cleaned_data['paddle_size']
                        match_point = form.cleaned_data['match_point']
                        is_3d = form.cleaned_data['is_3d']
                        tournament = Tournament.objects.create(size=size, num_users=1, ball_speed=ball_speed, paddle_size=paddle_size, match_point=match_point, is_3d=is_3d)
                        TournamentUser.objects.create(tournament=tournament, user=user)
                        request.session['tournament_id'] = tournament.id
                        page = 'tournament'
                        response_data = {
                            'page': page,
                            'content': read_file('waiting.html'),
                            'title': 'tournament',
                            'reload': page,
                            'timeout' : '10000',
                            'alert': '参加者を待っています',
                        }
                    else:
                        response_data = {
                            'page': page,
                            'content': render_to_string('customize_tournament.html', {'form': form, 'size': size}),
                            'title': 'customize game',
                        }
                else:
                    form = LoginForm(data=post_data)
                    response_data = {
                        'page': page,
                        'content': render_to_string('login.html', {'form': form, 'request': request}),
                        'title': 'Login',
                    }
            elif page == 'tournament':
                user = request.user
                tournament_id = request.session.get('tournament_id')
                thirty_seconds_ago = timezone.now() - timezone.timedelta(seconds=30)
                tournament_user = TournamentUser.objects.filter(user=user, timestamp__gte=thirty_seconds_ago, tournament=tournament_id).first()
                if tournament_user:
                    tournament_user.timestamp = timezone.now()
                    tournament_user.save()
                    tournament = tournament_user.tournament
                    num_users = TournamentUser.objects.filter(tournament=tournament, timestamp__gte=thirty_seconds_ago).count() #トーナメントが同じでtimestampが30秒以内のuserの数
                    tournament.num_users = num_users
                    tournament.save()
                    if num_users == tournament.size:
                        # logger.debug(f'user: {user}')
                        tournament_user.is_complete = True
                        tournament_user.save()
                        room = Matchmaking.objects.filter(user1=user, tournament=tournament, level=1).first()
                        if room:
                            if room.user2: #user2が存在していたら                                
                                response_data = {
                                    'page':page,
                                    'content':render_to_string('ponggame.html', {'room': room}),
                                    'title': 'Pong Game ' + str(room.id),
                                    # 生のjavascriptを埋め込みたいとき
                                    'rawscripts': 'startGame(' + str(room.id) + ', 1,' +  str(request.user.id) + ', 0, ' + str(room.paddle_size) + ', \'' + str(room.is_3d) + '\', ' + str(room.parent.id) + ', 0)',
                                }
                            else:
                                response_data = {
                                    'page': page,
                                    'content': read_file('waiting.html'),
                                    'title': 'tournament',
                                    'reload': page,
                                    'timeout' : '10000',
                                    'alert': '参加者を待っています',
                                }
                        else:
                            room = Matchmaking.objects.filter(user1__isnull=True, tournament=tournament, level=1).first()
                            if room: #tournamentとlevelが同じでuser1が不在のroom
                                # logger.debug('in tournament')
                                # logger.debug(f'user: {user}')       
                                room.user1 = user
                                room.save()
                                response_data = {
                                    'page': page,
                                    'content': read_file('waiting.html'),
                                    'title': 'tournament',
                                    'reload': page,
                                    'timeout' : '10000',
                                    'alert': '参加者を待っています',
                                }
                            else: #tournamentとlevelが同じでuser1が存在しuser2が不在のroom
                                room = Matchmaking.objects.filter(user2__isnull=True, tournament=tournament, level=1).first()
                                room.user2 = user
                                room.save()
                                response_data = {
                                'page':page,
                                'content':render_to_string('ponggame.html', {'room': room}),
                                'title': 'Pong Game ' + str(room.id),
                                # 生のjavascriptを埋め込みたいとき
                                'rawscripts': 'startGame(' + str(room.id) + ', 2,' +  str(request.user.id) + ', 0, ' + str(room.paddle_size) + ', \'' + str(room.is_3d) + '\', ' + str(room.parent.id) + ', 0)',
                            }     
                    else:
                        response_data = {
                            'page': page,
                            'content': read_file('waiting.html'),
                            'title': 'tournament',
                            'reload': page,
                            'timeout' : '10000',
                            'alert': '参加者を待っています',
                        }
                else:
                    rooms = get_available_rooms(user)
                    tournaments = get_available_tournaments(user)
                    doubles = get_available_doubles(user)
                    final_matches = get_final_matches(user)
                    response_data = {
                        'page': page,
                        'content': render_to_string('lobby.html', {'rooms': rooms, 'tournaments': tournaments, 'final_matches': final_matches, 'doubles': doubles}),
                        'title': 'Lobby'
                    }
            elif page == 'join_tournament':
                user = request.user
                tournament_id = post_data.get('tournament_id')
                room = Matchmaking.objects.filter(
                    Q(user1=user) |
                    Q(user2=user),
                    level=2,
                    winner__isnull=True,
                    tournament=tournament_id
                    ).first()
                if room: # 決勝戦の場合
                    gameplayer = 1
                    if room.user2 == user:
                        gameplayer = 2
                    response_data = {
                        'page':page,
                        'content':render_to_string('ponggame.html', {'room': room}),
                        'title': 'Pong Game ' + str(room.id),
                        'gameid': str(room.id), 
                        # 生のjavascriptを埋め込みたいとき
                        'rawscripts': 'startGame(' + str(room.id) + ', ' + str(gameplayer) + ',' +  str(request.user.id) + ', 0, ' + str(room.paddle_size) + ', \'' + str(room.is_3d) + '\', ' + str('0') + ', 0)',
                    }
                    return JsonResponse(response_data)
                thirty_seconds_ago = timezone.now() - timezone.timedelta(seconds=30)
                tournament = Tournament.objects.filter(id=tournament_id, timestamp__gte=thirty_seconds_ago).first()
                if not tournament: #存在しないトーナメント　→　タイムアウトで削除されている　→　ロビーへリダイレクト
                    rooms = get_available_rooms(user)
                    tournaments = get_available_tournaments(user)
                    doubles = get_available_doubles(user)
                    final_matches = get_final_matches(user)
                    response_data = {
                        'page': page,
                        'content': render_to_string('lobby.html', {'rooms': rooms, 'tournaments': tournaments, 'final_matches': final_matches, 'doubles': doubles}),
                        'title': 'Lobby',
                        'isValid': 'False',
                        'elem': 'tournament'
                    }
                    return JsonResponse(response_data)
                room = Matchmaking.objects.filter(
                    Q(user1=user) |
                    Q(user2=user),
                    level=1,
                    winner__isnull=True,
                    tournament=tournament
                ).first()
                # room = Matchmaking.objects.filter(tournament=tournament).first()
                if room: #すでにトーナメントが成立してる
                    room.timestamp = timezone.now()
                    room.save()
                    tournament.timestamp = timezone.now()
                    tournament.save()
                    tournament_user = TournamentUser.objects.filter(tournament=tournament, user=user).first()
                    tournament_user.timestamp = timezone.now()
                    tournament_user.save()
                    gameplayer = 1
                    if room.user2 == user:
                        gameplayer = 2
                    response_data = {
                            'page':page,
                            'content':render_to_string('ponggame.html', {'room': room}),
                            'title': 'Pong Game ' + str(room.id),
                            'gameid': str(room.id), 
                            # 生のjavascriptを埋め込みたいとき
                            'rawscripts': 'startGame(' + str(room.id) + ', ' + str(gameplayer) + ',' +  str(request.user.id) + ', 0, ' + str(room.paddle_size) + ', \'' + str(room.is_3d) + '\', ' + str(room.parent.id) + ', 1)',
                        }
                else: #トーナメント未成立
                    tournament_user = TournamentUser.objects.filter(tournament=tournament, user=user).first()
                    if tournament_user: #トーナメント内に同一のユーザーがいる
                        tournament_user.timestamp = timezone.now()
                        tournament_user.save()
                    else: #トーナメント内に新たなユーザーが参加
                        tournament_user = TournamentUser.objects.create(tournament=tournament, user=user)
                    num_users = TournamentUser.objects.filter(tournament=tournament, timestamp__gte=thirty_seconds_ago).count()
                    tournament.num_users = num_users 
                    tournament.save()
                    request.session['tournament_id'] = tournament.id
                    if num_users == tournament.size:
                        tournament_user.is_complete = True
                        tournament_user.save()
                        make_tournament_matches(tournament)
                        room = Matchmaking.objects.filter(user1__isnull=True, tournament=tournament, level=1).first()
                        gameplayer = 1
                        if room:
                            # logger.debug('in join tournament')
                            # logger.debug(f'user: {user}')
                            room.user1 = user
                            room.save()
                            page = 'tournament'
                            response_data = {
                                'page': page,
                                'content': read_file('waiting.html'),
                                'title': 'tournament',
                                'reload': page,
                                'timeout' : '10000',
                                'alert': '参加者を待っています',
                            }
                        else:
                            room = Matchmaking.objects.filter(user2__isnull=True, tournament=tournament, level=1).first()
                            room.user2 = user
                            room.save()
                            gameplayer = 2
                            response_data = {
                                'page':page,
                                'content':render_to_string('ponggame.html', {'room': room}),
                                'title': 'Pong Game ' + str(room.id),
                                'gameid': str(room.id), 
                                # 生のjavascriptを埋め込みたいとき
                                'rawscripts': 'startGame(' + str(room.id) + ', ' + str(gameplayer) + ',' +  str(request.user.id) + ', 0, ' + str(room.paddle_size) + ', \'' + str(room.is_3d) + '\', ' + str(room.parent.id) + ', 0)',
                            }
                    else:
                        page = 'tournament'
                        response_data = {
                            'page': page,
                            'content': read_file('waiting.html'),
                            'title': 'tournament',
                            'reload': page,
                            'timeout' : '10000',
                            'alert': '参加者を待っています',
                        }
            elif page == 'single_play':
                form = CustomizeSinglePlayForm(data=post_data)
                if form.is_valid():
                    ball_speed = form.cleaned_data['ball_speed']
                    paddle_size = form.cleaned_data['paddle_size']
                    match_point = form.cleaned_data['match_point']
                    is_3d = form.cleaned_data['is_3d']
                    ai = form.cleaned_data['ai']
                    room = Matchmaking.objects.create(user1=request.user, ball_speed=ball_speed, paddle_size=paddle_size, match_point=match_point, is_3d=is_3d, ai=ai, is_single=True)
                    response_data = {
                        'page':page,
                        'content':render_to_string('ponggame.html', {'room': room}),
                        'title': 'Pong Game ' + str(room.id),
                        'gameid': str(room.id), 
                        # 生のjavascriptを埋め込みたいとき
                        'rawscripts': 'startGame(' + str(room.id) + ', 1,' + str(request.user.id) + ', 0, ' + str(room.paddle_size) + ', \'' + str(room.is_3d) + '\', 0, 0)',
                    }
                else:
                    response_data = {
                        'page': page,
                        'content': render_to_string('customize_single_play.html', {'form': form}),
                        'title': 'customize single play'
                    }
            elif page == 'match_history':
                user = request.user
                if user.is_authenticated:
                    user_id = post_data.get('user_id')
                    if user_id:
                        user = CustomUser.objects.filter(id=user_id).first()
                        # logger.debug(f'user: {user}') 
                    matches = Matchmaking.objects.filter(is_single=False).exclude(winner__isnull=True)
                    tournaments = Tournament.objects.filter(size=F('num_users'))
                    tournament_users = TournamentUser.objects.filter(is_complete=True)
                    response_data = {
                            'page': page,
                            'content': render_to_string('match_history.html', {'user': user, 'matches': matches, 'tournaments': tournaments, 'tournament_users': tournament_users}),
                            'title': 'customize single play'
                        }
                else:
                    form = LoginForm(data=post_data)
                    response_data = {
                        'page': page,
                        'content': render_to_string('login.html', {'form': form, 'request': request}),
                        'title': 'Login',
                    }
            elif page == 'create_doubles':
                user = request.user
                if user.is_authenticated:
                    form = CustomizeDoublesForm(data=post_data)
                    if form.is_valid():
                        ball_speed = form.cleaned_data['ball_speed']
                        paddle_size = form.cleaned_data['paddle_size']
                        match_point = form.cleaned_data['match_point']
                        is_3d = form.cleaned_data['is_3d']
                        doubles = Doubles.objects.create(ball_speed=ball_speed, paddle_size=paddle_size, match_point=match_point, is_3d=is_3d)
                        DoublesUser.objects.create(doubles=doubles, user=user)
                        request.session['doubles_id'] = doubles.id
                        page = 'doubles_room'
                        response_data = {
                            'page': page,
                            'content': read_file('waiting.html'),
                            'title': 'doubles room',
                            'reload': page,
                            'timeout' : '10000',
                            'alert': '対戦相手を待っています',
                        }
                    else:
                        response_data = {
                            'page': page,
                            'content': render_to_string('customize_doubles.html', {'form': form}),
                            'title': 'customize doubles'
                        }
                else:
                    form = LoginForm(data=post_data)
                    response_data = {
                        'page': page,
                        'content': render_to_string('login.html', {'form': form, 'request': request}),
                        'title': 'Login',
                    }
            elif page == 'doubles_room':
                user = request.user
                doubles_id = request.session.get('doubles_id')
                thirty_seconds_ago = timezone.now() - timezone.timedelta(seconds=30)
                doubles_user = DoublesUser.objects.filter(user=user, is_complete=False, timestamp__gte=thirty_seconds_ago, doubles=doubles_id).first()            
                if doubles_user:
                    doubles_user.timestamp = timezone.now()
                    doubles_user.save()
                    doubles = doubles_user.doubles
                    num_users = DoublesUser.objects.filter(doubles=doubles, timestamp__gte=thirty_seconds_ago).count()
                    # logger.debug(f'num_users: {num_users}')
                    doubles.num_users = num_users
                    doubles.save()
                    if num_users == 4:
                        doubles_user.save()
                        room = Matchmaking.objects.filter(doubles=doubles).first()
                        user_no = 0
                        if not room:
                            room = Matchmaking.objects.create(user1=user, doubles=doubles, level=0)
                        else:
                            if not room.user2:
                                room.user2 = user
                            elif not room.user3:
                                room.user3 = user
                            elif not room.user4:
                                room.user4 = user
                            room.save()
                        if room.user1 and room.user2 and room.user3 and room.user4:
                            doubles_user.is_complete = True
                            if user == room.user1:
                                user_no = 1
                            elif user == room.user2:
                                user_no = 2
                            elif user == room.user3:
                                user_no = 3
                            else:
                                user_no = 4
                            response_data = {
                                'page':page,
                                'content':render_to_string('ponggame.html', {'room': room}),
                                'title': 'Pong Game ' + str(room.id),
                                'gameid': str(room.id), 
                                # 生のjavascriptを埋め込みたいとき
                                'rawscripts': 'startGame(' + str(room.id) + ', ' + str(user_no) + ', ' +  str(user.id) + ', 1, ' + str(room.paddle_size) + ', \'' + str(room.is_3d) + '\', 0, 0)',        
                            }
                        else:
                            response_data = {
                            'page': page,
                            'content': read_file('waiting.html'),
                            'title': 'doubles room',
                            'reload': page,
                            'timeout' : '10000',
                            'alert': '参加者を待っています',
                        }
                    else:
                        response_data = {
                            'page': page,
                            'content': read_file('waiting.html'),
                            'title': 'doubles room',
                            'reload': page,
                            'timeout' : '10000',
                            'alert': '参加者を待っています',
                        }
                else:
                    rooms = get_available_rooms(user)
                    tournaments = get_available_tournaments(user)
                    doubles = get_available_doubles(user)
                    final_matches = get_final_matches(user)
                    response_data = {
                        'page': page,
                        'content': render_to_string('lobby.html', {'rooms': rooms, 'tournaments': tournaments, 'final_matches': final_matches, 'doubles': doubles}),
                        'title': 'Lobby'
                    }
            elif page == 'join_doubles':
                user = request.user
                doubles_id = post_data.get('doubles_id')
                thirty_seconds_ago = timezone.now() - timezone.timedelta(seconds=30)
                doubles = Doubles.objects.filter(id=doubles_id, timestamp__gte=thirty_seconds_ago).first()
                if not doubles: #存在しないはずのダブルス
                    rooms = get_available_rooms(user)
                    tournaments = get_available_tournaments(user)
                    doubles = get_available_doubles(user)
                    final_matches = get_final_matches(user)
                    # logger.debug('hoge')
                    response_data = {
                        'page': page,
                        'content': render_to_string('lobby.html', {'rooms': rooms, 'tournaments': tournaments, 'final_matches': final_matches, 'doubles': doubles}),
                        'title': 'Lobby',
                        'isValid': 'False',
                        'elem': 'doubles'
                    }
                    return JsonResponse(response_data)
                room = Matchmaking.objects.filter(doubles=doubles).first() 
                if room: #すでにダブルスが成立してる
                    user_no = 1
                    if user.id == room.user2_id:
                        user_no = 2
                    elif user.id == room.user3_id:
                        user_no = 3
                    elif user.id == room.user4_id:
                        user_no = 4
                    # else :
                    #     user_no = 1

                    room.timestamp = timezone.now()
                    room.save()
                    doubles.timestamp = timezone.now()
                    doubles.save()
                    doubles_user = DoublesUser.objects.filter(doubles=doubles, user=user).first()
                    doubles_user.timestamp = timezone.now()
                    doubles_user.save()
                    response_data = {
                        # 'page':page,
                        # 'content':read_file('ponggame.html'),
                        # 'title': title,
                        # 'scriptfiles': '/static/js/game.js',
                        'page':page,
                        'content':render_to_string('ponggame.html', {'room': room}),
                        'title': 'Pong Game ' + str(room.id),
                        'gameid': str(room.id), 
                        'rawscripts': 'startGame(' + str(room.id) + ', ' + str(user_no) + ', ' +  str(user.id) + ', 1, ' + str(room.paddle_size) + ', \'' + str(room.is_3d) + '\', 0, 1)', 
                    }
                else: #まだマッチが成立してない
                    doubles_user = DoublesUser.objects.filter(doubles=doubles, user=user).first()
                    if doubles_user: #ダブルス内に同じユーザーがいる
                        doubles_user.timestamp = timezone.now()
                        doubles_user.save()
                    else:
                        doubles_user = DoublesUser.objects.create(doubles=doubles, user=user)
                    request.session['doubles_id'] = doubles.id
                    page = 'doubles_room'
                    response_data = {
                        'page': page,
                        'content': read_file('waiting.html'),
                        'title': 'doubles room',
                        'reload': page,
                        'timeout' : '10000',
                        'alert': '参加者を待っています',
                    }
            elif page == 'game_stats':
                user = request.user
                if user.is_authenticated:
                    users = CustomUser.objects.exclude(display_name__isnull=True)
                    response_data = {
                        'page': page,
                        'content': render_to_string('game_stats.html', {'users': users}),
                        'title': 'game stats',
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

@login_required
def gameHeartbeat(request, roomid):
    user = request.user
    room = Matchmaking.objects.get(id=roomid)
    if room:
        room.timestamp = timezone.now()
        room.save()
        if room.tournament:
            tournament = room.tournament
            tournament.timestamp = timezone.now()
            tournament.save()
        if room.doubles:
            doubles = room.doubles
            doubles.timestamp = timezone.now()
            doubles.save()
    return JsonResponse({'timestamp': 'refreshed'})

def get_csrf_token(request):
    token = get_token(request)
    return JsonResponse({'csrfToken': token})

@csrf_exempt
def setLanguage(request, lang):
    user = request.user
    if user.is_authenticated:
        user.language = lang
        user.save()
        return JsonResponse({'status': 'language_saved'})
    return JsonResponse({'status': 'not_login'})

@csrf_exempt
def getLanguage(request, lang):
    user = request.user
    if user.is_authenticated:
        tmplang = user.language
        # デフォルトでDBにjaが入ってないらしい
        if tmplang == "" :
            user.language = lang
        lang = tmplang
    elif lang == '00' :
        lang = 'ja'
    # logger.debug(lang)
    return HttpResponse(read_translations(lang + '.json'))

@csrf_exempt
def upload_image(request):
    if request.method == 'POST':
        try:
            #受信データの処理            
            form = ImageForm(request.POST, request.FILES)
            if form.is_valid():
                avatar = request.FILES.get('image') # アップロードされた画像ファイルを取得
                if avatar:
                    user = request.user
                    img = PilImage.open(avatar) # 画像を開く
                    img = img.resize((128, 128), Image.Resampling.LANCZOS) # 画像を128x128にリサイズ
                    # 画像を保存するためのメモリストリームを用意
                    img_io = BytesIO()
                    img.save(img_io, format='PNG', quality=100)
                    img_io.seek(0)
                    img_content = ContentFile(img_io.getvalue()) # メモリストリームからContentFileを作成
                    form.cleaned_data['image'].file = img_content # ContentFileをフォームのImageFieldに設定
                image_instance = form.save()
                response_data = {
                    'msgtagid':'result',
                    'imgtagid':'uploaded',
                    'imgsrc':'media/' + image_instance.image.name,
                    'descimage':'アップロード画像',
                    'setid': 'id_avatar',
                    'setvalue': image_instance.image.name,
#                    'exec':'document.getElementById(\'id_avatar\').value = "' + image_instance.image.name + '"',
                }
                return JsonResponse(response_data)
            else:
                lang = request.user.language
                if lang == 'en':    
                    return JsonResponse({'error': 'Invalid data'}, status=400)
                elif lang == 'kr':
                    return JsonResponse({'error': '부정한 데이터입니다'}, status=400)
                else:
                    return JsonResponse({'error': '不正なデータです'}, status=400)
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

@csrf_exempt
def read_translations(filename):
    # プロジェクトのベースディレクトリを取得
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # ファイルのパスを構築
    file_path = os.path.join(base_dir, 'main/static/translations', filename)
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return "Error: File not found."
    except Exception as e:
        return f"Error: {e}"


def get_available_rooms(user):
    current_time = timezone.now()
    thirty_seconds_ago = current_time - timedelta(seconds=30)
    available_rooms = Matchmaking.objects.filter(
        Q(user2__isnull=True) | Q(user1=user) | Q(user2=user), #user2が不在かuser1かuser2がuserと同じ
        timestamp__gte=thirty_seconds_ago, #timest.exam.expから30秒以内
        is_single=False,
        winner__isnull=True,
        tournament__isnull=True,
        doubles__isnull=True,
        level=-1,
    )
    return available_rooms

#num_usersがsizeより小さくtimestampから30秒以内のtournamentを取得
def get_available_tournaments(user):
    current_time = timezone.now()
    thirty_seconds_ago = current_time - timedelta(seconds=30)
    available_tournaments = Tournament.objects.filter(
        Q(num_users__lt=F('size')) | #unm_usersがsizeより少ない
        (Q(num_users=F('size')) & Q( #num_usersがsizeと同じでuser1か2にuserがいてwinnerがnull
            Q(matchmaking__user1=user) | 
            Q(matchmaking__user2=user),
            matchmaking__winner__isnull=True,
            matchmaking__level=1
        )),
        timestamp__gte=thirty_seconds_ago
    )
    return available_tournaments

def get_final_matches(user):
    final_matches = Tournament.objects.filter(
        Q(matchmaking__user1=user) |
        Q(matchmaking__user2=user),
        matchmaking__level=2,
        matchmaking__winner__isnull=True,
    )
    return final_matches

# def get_available_doubles(user):
#     current_time = timezone.now()
#     thirty_seconds_ago = current_time - timedelta(seconds=30)
#     available_doubles = Doubles.objects.filter(
#         Q(num_users__lt=4) | #参加者が4人未満
#         (Q(num_users=4) & Q( #参加者が4人いてuser1-4にuserがいてwinnerがnull
#             Q(matchmaking__user1=user) | 
#             Q(matchmaking__user2=user) | 
#             Q(matchmaking__user3=user) | 
#             Q(matchmaking__user4=user),
#             matchmaking__winner__isnull=True,
#         )),
#         timestamp__gte=thirty_seconds_ago
#     )
#     # logger.debug(f'available_doubles: {available_doubles}')
#     return available_doubles

def get_available_doubles(user):
    current_time = timezone.now()
    thirty_seconds_ago = current_time - timedelta(seconds=30)

    available_doubles = Doubles.objects.annotate(
        point_diff=ExpressionWrapper(
            F('matchmaking__point1') - F('matchmaking__point2'),
            output_field=IntegerField()
        )
    ).filter(
        Q(num_users__lt=4) |  # 参加者が4人未満
        (Q(num_users=4) & Q(  # 参加者が4人いて、user1-4にuserがいて、winnerがnull
            Q(matchmaking__user1=user) | 
            Q(matchmaking__user2=user) | 
            Q(matchmaking__user3=user) | 
            Q(matchmaking__user4=user),
            Q(
                Q(
                    Q(matchmaking__point1__gte=F('matchmaking__match_point')) | 
                    Q(matchmaking__point2__gte=F('matchmaking__match_point'))
                ) & Q(
                    Q(point_diff__gt=-1) &
                    Q(point_diff__lt=1)
                )
            ) |
            Q(
                Q(matchmaking__point1__lt=10) & 
                Q(matchmaking__point2__lt=10)
            )
        )),
        timestamp__gte=thirty_seconds_ago
    )
    return available_doubles

    
def make_tournament_matches(tournament):
    num_levels = ceil(log2(tournament.size))  # level数を計算(決勝戦はlog2(tournament.size)、初戦は1)、cielは切上
    level = num_levels
    final_match = Matchmaking.objects.create(tournament=tournament, user1=None, user2=None, level=level, ball_speed=tournament.ball_speed, paddle_size=tournament.paddle_size, match_point=tournament.match_point, is_3d=tournament.is_3d) #決勝戦
    current_matches = []
    current_matches.append(final_match)
    next_matches = []
    for _ in range(num_levels - 1): # 各ラウンドでのマッチを生成
        level -= 1
        while current_matches:
            parent = current_matches.pop(0)
            for _ in range(2):# 親に対して2つのマッチを生成
                match = Matchmaking.objects.create(tournament=tournament, parent=parent, user1=None, user2=None, level=level, ball_speed=tournament.ball_speed, paddle_size=tournament.paddle_size, match_point=tournament.match_point, is_3d=tournament.is_3d)
                next_matches.append(match)
        current_matches = next_matches
        next_matches = []

def calculate_loss(user, win):
    count1 = Matchmaking.objects.filter(user1=user, is_single=False).exclude(winner__isnull=True).count()
    count2 = Matchmaking.objects.filter(user2=user, is_single=False).exclude(winner__isnull=True).count()
    loss = count1 + count2 - win
    return loss

@login_required
def ja(request):
    # logger.debug('im here')
    return JsonResponse({'language': 'ja'})