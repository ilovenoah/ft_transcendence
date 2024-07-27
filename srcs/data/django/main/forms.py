from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from .models import Image


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254)

    class Meta:
        model = get_user_model() 
        fields = ('username', 'email', 'password1', 'password2')

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

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
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
    to_user = forms.ModelChoiceField(queryset=User.objects.all())
    def __init__(self, *args, **kwargs):
        self.from_user = kwargs.pop('from_user', None)
        super().__init__(*args, **kwargs)
        if self.from_user:
            self.fields['to_user'].queryset = User.objects.exclude(id=self.from_user.id)

class FriendRequestActionForm(forms.Form):
    action = forms.ChoiceField(choices=[('accept', 'Accept')])