from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
import re

class User(AbstractUser):
    username = models.CharField(
        "username",
        max_length=20,
        unique=True,
        error_messages=None,
        #validators=[username_validator] #https://docs.djangoproject.com/en/4.1/ref/forms/validation/
    )
    def clean(self): #TODO: předělat to do validatoru jako je níže
        super().clean()
        pattern = re.compile("^[a-zA-Z0-9-_.]+$")
        if not pattern.match(self.username):
            raise ValidationError("Username contains invalid character. Try again.", code="invalid")

class Feed(models.Model):
    name = models.CharField(max_length=20, validators=[RegexValidator("^[a-zA-Z0-9-_.]+$", "Špatně")]) #TODO: Text při chybě - mrknout do modelformu
    date_created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE) #, default=

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'owner'], name='unique name and owner bond')
        ]

class Data(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=12, decimal_places=3) #100 000 000,000
    date_created = models.DateTimeField(auto_now=True)
