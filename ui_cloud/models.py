from django.db import models
from django.contrib.auth.models import AbstractUser

from django.core.validators import RegexValidator

class User(AbstractUser):
    username = models.CharField(
        "username",
        max_length=20,
        unique=True,
        error_messages=None,
        validators=[RegexValidator("^[a-z0-9-_.]+$", 
                                   "Lowered username contains invalid character.")]
    )

    display_name = models.CharField(
        max_length=20,
        unique=True,
        validators=[RegexValidator("^[a-zA-Z0-9-_.]+$", 
                                   "Username contains invalid character.")],
        error_messages={"unique":"User with this username already exists."}
    )

    def __str__(self):
        return self.display_name