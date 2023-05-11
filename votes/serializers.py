from rest_framework import serializers

from restaurants.models import Menu


class VoteSerializer(serializers.Serializer):
    """
    Serializer for voting on a menu.
    """

    menu = serializers.PrimaryKeyRelatedField(queryset=Menu.objects.all())
    # The menu field represents the menu being voted on

    points = serializers.IntegerField(min_value=1, max_value=3)
    # The points field represents the number of points assigned to the menu vote
