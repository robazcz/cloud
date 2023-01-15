from rest_framework import serializers
from . import models

class UserSerialilzer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ["username", "email"]