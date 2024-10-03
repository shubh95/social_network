# logging_management/serializers.py

from rest_framework import serializers
from .models import Log

class LogListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = ['id', 'user', 'action', 'action_started_at', 'action_completed_at', 'status_code']

class LogDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = '__all__'


class LogCreateSerializer(serializers.Serializer):
    action = serializers.CharField()
    payload = serializers.JSONField(required=False)

    def validate(self, data):
        user_id = self.context.get('user_id')
        action = data.get('action')
        payload = data.get('payload')

        if not payload:
            payload = {}

        return {
            'user_id': user_id,
            'action': action,
            'payload': payload
        }
    
    def create(self, validated_data):
        log = Log.objects.create(
            user_id=validated_data['user_id'],
            action=validated_data['action'],
            payload=validated_data['payload']
        )
        return log
    
    def to_representation(self, instance):
        return {
            'id': instance.id,
            'user': instance.user.email,
            'action': instance.action,
            'payload': instance.payload,
            'ip_addr': instance.ip_addr,
            'action_started_at': instance.action_started_at
        }