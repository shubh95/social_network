# serializers
from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import FriendRequest

class FriendRequestSerializer(serializers.ModelSerializer):
    to_user = UserSerializer()

    class Meta:
        model = FriendRequest
        fields = '__all__'