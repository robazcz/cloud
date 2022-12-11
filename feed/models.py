from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
import re

class User(AbstractUser):
    def clean(self):
        super().clean()
        pattern = re.compile("^[a-zA-Z1-9]+$")
        if not pattern.match(self.username):
            raise ValidationError("username contains invalid character")

class Feed(models.Model):
    name = models.CharField(max_length=20)
    date_created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE) #, default=

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'owner'], name='unique name and owner bond')
        ]

class Data(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    value = models.CharField(max_length=20)
    date_created = models.DateTimeField(auto_now=True)
