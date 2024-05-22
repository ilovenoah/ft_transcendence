from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254)
    nickname = forms.CharField(max_length=255, required=False)

    class Meta:
        model = get_user_model()  # これにより、カスタムユーザーモデルが使用されます
        fields = ('username', 'email', 'nickname', 'password1', 'password2')

