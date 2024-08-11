from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from .models import Image, FriendRequest, CustomUser, Matchmaking, Tournament
import re
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models import Q



class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254)

    class Meta:
        model = get_user_model() 
        fields = ('username', 'email', 'password1', 'password2')

class LoginForm(AuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                # ログ出力で何が起きているかを確認
                print("Authentication failed: Username or password is incorrect.")
                raise forms.ValidationError(
                    _("ユーザー名またはパスワードが正しくありません"),
                    code='invalid_login',
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

User = get_user_model()

class UsernameForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username']
    def __init__(self, *args, **kwargs):
        super(UsernameForm, self).__init__(*args, **kwargs)
        self.fields['username'].required = True
        del self.fields['password'] # パスワードフィールドを削除する

class EmailForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['email']
    def __init__(self, *args, **kwargs):
        super(EmailForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True

class DisplayNameForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['display_name']
    def __init__(self, *args, **kwargs):
        super(DisplayNameForm, self).__init__(*args, **kwargs)
        self.fields['display_name'].required = True

class AvatarForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['avatar']
        widgets = {
            'avatar': forms.HiddenInput(),
        }
    def __init__(self, *args, **kwargs):
        super(AvatarForm, self).__init__(*args, **kwargs)
        self.fields['avatar'].required = True

class PasswordChangeForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirm password")

    class Meta:
        model = User
        fields = ['password']

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise ValidationError('パスワードは8文字以上である必要があります')
        if not re.findall('[a-zA-Z]', password):
            raise ValidationError('パスワードには少なくとも一つの文字が含まれている必要があります')
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "同一のパスワードではありません")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']

class FriendRequestForm(forms.Form):
    to_user = forms.ModelChoiceField(queryset=CustomUser.objects.all(), label="Add Friend", required=False)

    def __init__(self, *args, **kwargs):
        self.from_user = kwargs.pop('from_user', None)
        super().__init__(*args, **kwargs)
        if self.from_user:
            # すでに友達申請を送ったユーザーとすでに友達になっているユーザーを取得
            pending_or_accepted_requests = FriendRequest.objects.filter(
                Q(from_user=self.from_user) | Q(to_user=self.from_user),
                Q(status='P') | Q(status='A')
            ).values_list('from_user', 'to_user')

            # 除外するユーザーのIDリストを作成
            excluded_user_ids = set()
            for from_user_id, to_user_id in pending_or_accepted_requests:
                if from_user_id != self.from_user.id:
                    excluded_user_ids.add(from_user_id)
                if to_user_id != self.from_user.id:
                    excluded_user_ids.add(to_user_id)

            # 自分自身、display_nameがNone、すでに友達申請を送ったまたはすでに友達になっているユーザーを除外
            self.fields['to_user'].queryset = CustomUser.objects.exclude(
                id__in=excluded_user_ids
            ).exclude(
                id=self.from_user.id
            ).exclude(
                display_name=None
            ).order_by('display_name')

        self.fields['to_user'].label_from_instance = self.label_from_instance

    def label_from_instance(self, obj):
        return obj.display_name


class FriendRequestActionForm(forms.Form):
    action = forms.ChoiceField(choices=[('accept', 'Accept')])

class CustomizeGameForm(forms.ModelForm):
    BALL_SPEED_CHOICES = [
        (2, '標準'),
        (1, '遅い'),
        (3, '速い'),
    ]
    ball_speed = forms.ChoiceField(choices=BALL_SPEED_CHOICES)

    PADDLE_SIZE_CHOICES = [
        (2, '標準'),
        (1, '小さい'),
        (3, '大きい'),
    ]
    paddle_size = forms.ChoiceField(choices=PADDLE_SIZE_CHOICES)

    MATCH_POINT_CHOICES = [
        (10, '10'),
        (15, '15'),
        (20, '20'),
    ]
    match_point = forms.ChoiceField(choices=MATCH_POINT_CHOICES)

    IS_3D_CHOICES = [
        (False, '2D'),
        (True, '3D'),
    ]
    is_3d = forms.ChoiceField(choices=IS_3D_CHOICES)

    class Meta:
        model = Matchmaking
        fields = ['ball_speed', 'paddle_size', 'match_point', 'is_3d']
    
class CustomizeSinglePlayForm(forms.ModelForm):
    BALL_SPEED_CHOICES = [
        (2, '標準'),
        (1, '遅い'),
        (3, '速い'),
    ]
    ball_speed = forms.ChoiceField(choices=BALL_SPEED_CHOICES)

    PADDLE_SIZE_CHOICES = [
        (2, '標準'),
        (1, '小さい'),
        (3, '大きい'),
    ]
    paddle_size = forms.ChoiceField(choices=PADDLE_SIZE_CHOICES)

    MATCH_POINT_CHOICES = [
        (10, '10'),
        (15, '15'),
        (20, '20'),
    ]
    match_point = forms.ChoiceField(choices=MATCH_POINT_CHOICES)

    IS_3D_CHOICES = [
        (False, '2D'),
        (True, '3D'),
    ]
    is_3d = forms.ChoiceField(choices=IS_3D_CHOICES)

    AI_CHOICES = [
        (2, "普通"),
        (1, "弱い"),
        (3, "強い"),
    ]
    ai = forms.ChoiceField(choices=AI_CHOICES)

    class Meta:
        model = Matchmaking
        fields = ['ball_speed', 'paddle_size', 'match_point', 'is_3d', 'ai']

class CustomizeTournamentForm(forms.ModelForm):
    BALL_SPEED_CHOICES = [
        (2, '標準'),
        (1, '遅い'),
        (3, '速い'),
    ]
    ball_speed = forms.ChoiceField(choices=BALL_SPEED_CHOICES)

    PADDLE_SIZE_CHOICES = [
        (2, '標準'),
        (1, '小さい'),
        (3, '大きい'),
    ]
    paddle_size = forms.ChoiceField(choices=PADDLE_SIZE_CHOICES)

    MATCH_POINT_CHOICES = [
        (10, '10'),
        (15, '15'),
        (20, '20'),
    ]
    match_point = forms.ChoiceField(choices=MATCH_POINT_CHOICES)

    IS_3D_CHOICES = [
        (False, '2D'),
        (True, '3D'),
    ]
    is_3d = forms.ChoiceField(choices=IS_3D_CHOICES)

    class Meta:
        model = Tournament
        fields = ['ball_speed', 'paddle_size', 'match_point', 'is_3d']