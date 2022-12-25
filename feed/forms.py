from django import forms
from . import models

class LoginForm(forms.ModelForm):
    #template_name = "feed/form_snippet.html" #TODO: Custom template
    class Meta:
        model = models.User
        fields = ["username", "password"]

        widgets = {
            "password": forms.PasswordInput(),
            "username": forms.TextInput()
        }