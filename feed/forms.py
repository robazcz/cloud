from django import forms
from django.contrib.auth import forms as authforms
from django.db import IntegrityError

from . import models

class LoginForm(authforms.AuthenticationForm):
    template_name = "form_snippet.html" #Custom template
    # class Meta:
    #     model = models.User
    #     fields = ["username", "password"]
    #
    #     widgets = {
    #         "password": forms.PasswordInput(),
    #         #"username": forms.TextInput()
    #     }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["placeholder"] = "Username"
        self.fields["password"].widget.attrs["placeholder"] = "Password"


class NewFeed(forms.ModelForm):
    template_name = "form_snippet.html"
    class Meta:
        model = models.Feed
        fields = ["name"]

    def save(self, *args, **kwargs):
        try:
            res = super().save(*args, **kwargs)
        except IntegrityError as err:
            self.add_error("name", "This name already exists for save")
            raise IntegrityError(err)

        return res

class RegisterForm(authforms.UserCreationForm):
    template_name = "form_snippet.html"  # Custom template
    class Meta(authforms.UserCreationForm.Meta):
        model = models.User
        fields = ["username_original"]
        field_classes = {"username_original": authforms.UsernameField}
        labels = {"username_original":"Username"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username_original"].label = "Username"
        self.fields["password1"].label = "Password"
        self.fields["password2"].label = "Confirm_password"
        self.fields["username_original"].widget.attrs["placeholder"] = "Username"
        self.fields["password1"].widget.attrs["placeholder"] = "Password"
        self.fields["password2"].widget.attrs["placeholder"] = "Confirm password"

    def save(self, *args, **kwargs):
        try:
            res = super().save(*args, **kwargs)
        except IntegrityError as err:
            if str(err) == "UNIQUE constraint failed: feed_user.username":
                raise IntegrityError("Username exists")
            raise IntegrityError(err)

        return res