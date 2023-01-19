from rest_framework import serializers
from . import models

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ["username", "email"]

class DataSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Data
        fields = ["value", "date_created"]