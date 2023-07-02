from django.db import models
from django.contrib.auth.models import AbstractUser

from django.core.validators import RegexValidator
from django.utils.timezone import now

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
    
class Feed(models.Model):
    name = models.CharField(max_length=20, 
                            validators=[RegexValidator("^[a-zA-Z0-9-_.]+$", "Feeds name contains invalid character.")],
                            error_messages={"unique_name_owner": "Already exists"})
    date_created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'owner'],
                                    name='unique_name_owner', 
                                    violation_error_message="Exists")
        ]

    def __str__(self):
        return self.name
    
class Data(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=12, decimal_places=3) #100 000 000,000
    date_created = models.DateTimeField(default=now)