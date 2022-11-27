from django.db import models
# from django.contrib.auth.models import AbstractUser

# class User(AbstractUser):
#     pass

class Feed(models.Model):
    name = models.CharField(max_length=20, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)

class Data(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    value = models.CharField(max_length=20)
    date_created = models.DateTimeField(auto_now=True)
