from django import forms
from . import models

class LoginForm(forms.ModelForm):
    template_name = "form_snippet.html" #Custom template
    class Meta:
        model = models.User
        fields = ["username", "password"]

        widgets = {
            "password": forms.PasswordInput(),
            #"username": forms.TextInput()
        }

class NewFeed(forms.ModelForm):
    # template_name = "form_snippet.html"
    class Meta:
        model = models.Feed
        fields = ["name"]