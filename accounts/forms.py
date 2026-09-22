from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class createuserform(UserCreationForm):

    class Meta:
        model = User
        fields = ['email', 'username', 'password1', 'password2']