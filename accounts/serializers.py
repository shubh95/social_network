# serializers.py
from rest_framework import serializers
from .models import CustomUser, BlockedUser

from friend_management.utils import FriendshipManager

class UserSerializer(serializers.ModelSerializer):
    is_blocked = serializers.SerializerMethodField()
    is_friend = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'is_active', 'is_staff', 'first_name', 'last_name', 'is_blocked', 'is_friend')
    
    def get_is_blocked(self, obj):
        request_user = self.context['request_user']
        return BlockedUser.objects.filter(user=request_user, blocked_user=obj).exists()
    
    def get_is_friend(self, obj):
        request_user = self.context['request_user']
        return FriendshipManager.are_friends(request_user, obj)


class MyselfSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'role')


class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'role')
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def validate(self, data):
        if CustomUser.objects.search_by_email(data['email']).exists():
            raise serializers.ValidationError('Email already exists')
        return data

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        user.first_name = validated_data.get('first_name', '')
        user.last_name = validated_data.get('last_name', '')
        user.role = validated_data.get('role', 'read')
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()


class BlockedUserListSerializer(serializers.ModelSerializer):
    blocked_user = UserSerializer()
    
    class Meta:
        model = BlockedUser
        fields = '__all__'
    
    def get_serializer_context(self):
        return {'request_user': self.context['request_user']}

class BlockedUserCreateSerializer(serializers.Serializer):
    blocked_user = serializers.IntegerField()

    def validate(self, data):
        user_id = self.context['user_id']
        data['user_id'] = user_id
        blocked_user_id = data.get('blocked_user')

        if user_id == blocked_user_id:
            raise serializers.ValidationError('You cannot block yourself')
        
        if BlockedUser.objects.filter(user_id=user_id, blocked_user_id=blocked_user_id).exists():
            raise serializers.ValidationError('User is already blocked')

        if CustomUser.objects.filter(id=blocked_user_id).exists():
            return data

        raise serializers.ValidationError('Invalid user id')
    
    def create(self, validated_data):
        user = CustomUser.objects.get(id=validated_data['user_id'])
        blocked_user = CustomUser.objects.get(id=validated_data['blocked_user_id'])
        BlockedUser.objects.create(user=user, blocked_user=blocked_user)
        return user
        
