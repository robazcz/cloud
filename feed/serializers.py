from rest_framework import serializers
from . import models

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ["username", "email"]
        read_only_fields = fields

class DataSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Data
        fields = ["value", "date_created"]

class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Feed
        fields = ["id", "name", "date_created"]
