from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    terms = forms.BooleanField(required=True)
    newsletter = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "terms", "newsletter")
