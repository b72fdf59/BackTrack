from django.contrib.auth.models import User, Group
from .models import PBI
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class PBISerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PBI
        fields = ['url', 'summary', 'status', 'story_points', 'effort_hours','priority']
