from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
import re

from django.db.models.functions import Lower


class User(AbstractUser):
    username = models.CharField(
        "username",
        max_length=20,
        unique=True,
        error_messages=None,
        validators=[RegexValidator("^[a-z0-9-_.]+$", "Lowered username contains invalid character.")]
        #validators=[username_validator] #https://docs.djangoproject.com/en/4.1/ref/forms/validation/
    )
    username_original = models.CharField(
        max_length=20,
        unique=True,
        validators=[RegexValidator("^[a-zA-Z0-9-_.]+$", "Username contains invalid character.")],
        error_messages={"unique":"User with this username already exists."}
    )

    def __str__(self):
        return self.username_original

    class Meta:
        pass
        # constraints = [  # TODO: https://stackoverflow.com/questions/36330677/django-model-set-default-charfield-in-lowercase ## zachovat velikosti registrace?
        #     models.UniqueConstraint(Lower("username"), name="unique_lower_username")
        # ]
    # def clean(self): #validace jiným způsobem
    #     super().clean()
    #     pattern = re.compile("^[a-zA-Z0-9-_.]+$")
    #     if not pattern.match(self.username):
    #         raise ValidationError("Username contains invalid character. Try again.", code="invalid")

class Feed(models.Model):
    name = models.CharField(max_length=20, validators=[RegexValidator("^[a-zA-Z0-9-_.]+$",
                                                                      "Feeds name contains invalid character.")],
                            error_messages={"unique_name_owner": "Already exists"})
    date_created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE) #, default=

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'owner'], name='unique_name_owner', violation_error_message="Exists")
        ]

class Data(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=12, decimal_places=3) #100 000 000,000
    date_created = models.DateTimeField(default=now)


    # def save(self, *args, **kwargs):
    #     if self.value == "NaN":
    #         raise ValidationError("NaN")
    #     super().save(self, *args, **kwargs)