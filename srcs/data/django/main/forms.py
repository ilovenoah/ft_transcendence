from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254)

    class Meta:
        model = get_user_model() 
        fields = ('username', 'email', 'password1', 'password2')

class CustomUserChangeForm(UserChangeForm):
    password1 = forms.CharField(label='New password', widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label='Confirm new password', widget=forms.PasswordInput, required=False)

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'avatar', 'password1', 'password2')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password1")  # password1からパスワードを取得
        if password:  # 新しいパスワードが入力されているかを確認
            user.set_password(password)
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)
        self.fields.pop('password', None)  # password フィールドを削除
        # self.fields['email'].required = True
        # self.fields['avatar'].required = True

