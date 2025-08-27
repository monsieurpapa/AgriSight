from rest_framework import serializers
from .models import APIKey, AnalyticsLog


class APIKeySerializer(serializers.ModelSerializer):
    """Serializer for APIKey model."""
    
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = APIKey
        fields = [
            'id', 'organization', 'organization_name', 'key_name', 'key_prefix',
            'is_active', 'expires_at', 'last_used_at', 'permissions',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'key_prefix', 'last_used_at', 'created_at', 'updated_at']


class APIKeyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating APIKey instances."""
    
    class Meta:
        model = APIKey
        fields = ['organization', 'key_name', 'expires_at', 'permissions']


class AnalyticsLogSerializer(serializers.ModelSerializer):
    """Serializer for AnalyticsLog model."""
    
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = AnalyticsLog
        fields = [
            'id', 'organization', 'organization_name', 'user', 'username',
            'action_type', 'resource_type', 'resource_id', 'request_path',
            'response_time_ms', 'status_code', 'ip_address', 'user_agent',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UsageStatsSerializer(serializers.Serializer):
    """Serializer for usage statistics."""
    
    total_requests = serializers.IntegerField()
    requests_by_action = serializers.DictField()
    requests_by_resource = serializers.DictField()
    avg_response_time = serializers.FloatField()
    error_rate = serializers.FloatField()
    top_users = serializers.ListField()

