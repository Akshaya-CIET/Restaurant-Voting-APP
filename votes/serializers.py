from rest_framework import serializers

from restaurants.models import Menu


class VoteSerializer(serializers.Serializer):
    menu = serializers.PrimaryKeyRelatedField(queryset=Menu.objects.all())
    points = serializers.IntegerField(min_value=1, max_value=3)
