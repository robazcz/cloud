from rest_framework import serializers
from . import models


class DataSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Data
        fields = ["value", "date_created"]


class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Feed
        fields = ["id", "name", "date_created"]
