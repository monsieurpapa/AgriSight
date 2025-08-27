from rest_framework import serializers
from .models import Report, Alert


class ReportSerializer(serializers.ModelSerializer):
    """Serializer for Report model."""
    
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    region_names = serializers.SerializerMethodField()
    
    class Meta:
        model = Report
        fields = [
            'id', 'title', 'organization', 'organization_name', 'regions',
            'region_names', 'report_type', 'time_period_start', 'time_period_end',
            'content', 'file_path', 'is_published', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_region_names(self, obj):
        """Get list of region names."""
        return list(obj.regions.values_list('name', flat=True))


class ReportCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Report instances."""
    
    class Meta:
        model = Report
        fields = [
            'title', 'organization', 'regions', 'report_type',
            'time_period_start', 'time_period_end', 'content', 'file_path'
        ]


class AlertSerializer(serializers.ModelSerializer):
    """Serializer for Alert model."""
    
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    region_names = serializers.SerializerMethodField()
    read_by_username = serializers.CharField(source='read_by.username', read_only=True)
    
    class Meta:
        model = Alert
        fields = [
            'id', 'organization', 'organization_name', 'regions', 'region_names',
            'alert_type', 'severity', 'title', 'message', 'related_stress_event',
            'related_conflict_event', 'is_read', 'read_by', 'read_by_username',
            'read_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_region_names(self, obj):
        """Get list of region names."""
        return list(obj.regions.values_list('name', flat=True))


class AlertCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Alert instances."""
    
    class Meta:
        model = Alert
        fields = [
            'organization', 'regions', 'alert_type', 'severity', 'title',
            'message', 'related_stress_event', 'related_conflict_event'
        ]


class AlertUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating Alert instances (mainly for marking as read)."""
    
    class Meta:
        model = Alert
        fields = ['is_read', 'read_by', 'read_at']

