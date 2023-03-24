from django import forms
from django.contrib.auth import forms as authforms
from django.db import IntegrityError

from . import models

class LoginForm(authforms.AuthenticationForm):
    template_name = "form_snippet.html" #Custom template

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["placeholder"] = "Username"
        self.fields["password"].widget.attrs["placeholder"] = "Password"

class RegisterForm(authforms.UserCreationForm):
    template_name = "form_snippet.html"  # Custom template
    class Meta(authforms.UserCreationForm.Meta):
        model = models.User
        fields = ["display_name"]
        field_classes = {"display_name": authforms.UsernameField}
        labels = {"display_name":"Username"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["display_name"].label = "Username"
        self.fields["password1"].label = "Password"
        self.fields["password2"].label = "Confirm_password"
        self.fields["display_name"].widget.attrs["placeholder"] = "Username"
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

class NewFeed(forms.ModelForm):
    template_name = "form_snippet.html"
    class Meta:
        model = models.Feed
        fields = ["name"]
        labels = {"name":""}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs["placeholder"] = "Name of field"

    def save(self, *args, **kwargs):
        try:
            res = super().save(*args, **kwargs)
        except IntegrityError as err:
            if str(err) == "UNIQUE constraint failed: feed_feed.name, feed_feed.owner_id":
                raise IntegrityError("Feed name exists")
            raise IntegrityError(err)

        return res

class OptionsForm(forms.Form):
    template_name = "form_snippet.html"
    limit_by = forms.ChoiceField(label= "", choices = (("number", "number of records"), ("date", "from date to date")))
    limit_number = forms.ChoiceField(label = "", required=False, choices = (("5", "5"), ("10", "10"), ("20", "20"), ("50", "50"), ("100", "100"), ("200", "200"), ("all", "all")))
    limit_date = forms.DateTimeField(label="", required=False)

    limit_date.widget.attrs.update({"placeholder": "Click to select date range"})

class DataForm(forms.ModelForm):
    template_name = "form_snippet.html"
    class Meta:
        model = models.Data
        fields = ["value"]
        labels = {"value": ""}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["value"].widget.attrs["placeholder"] = "0.000"