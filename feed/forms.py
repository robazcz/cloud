from django import forms
from django.contrib.auth import forms as authforms
from django.db import IntegrityError

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
    template_name = "form_snippet.html"
    class Meta:
        model = models.Feed
        fields = ["name"]

    def save(self, *args, **kwargs):
        try:
            res = super().save(*args, **kwargs)
        except IntegrityError as err:
            raise IntegrityError(err)

        return res

class RegisterForm(authforms.UserCreationForm):
    template_name = "form_snippet.html"  # Custom template
    class Meta(authforms.UserCreationForm.Meta):
        model = models.User
        fields = ["username_original"]
        field_classes = {"username_original": authforms.UsernameField}
        labels = {"username_original":"Username"}