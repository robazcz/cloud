from django import forms
from django.contrib.auth import forms as authforms

from .models import Feed, Data

class LoginForm(authforms.AuthenticationForm):
    pass

class FeedForm(forms.ModelForm):
    class Meta:
        model = Feed
        fields = ["name"]

class ValueForm(forms.ModelForm):
    class Meta:
        model = Data
        fields = ["value"]