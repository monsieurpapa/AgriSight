from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import AgriculturalStressEvent, ConflictEvent


class AgriculturalStressEventSerializer(GeoFeatureModelSerializer):
    """GeoJSON serializer for AgriculturalStressEvent model."""
    
    region_name = serializers.CharField(source='region.name', read_only=True)
    crop_name = serializers.CharField(source='crop_mapping.crop.name', read_only=True)
    evidence_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AgriculturalStressEvent
        geo_field = 'geometry'
        fields = [
            'id', 'region', 'region_name', 'crop_mapping', 'crop_name',
            'detection_date', 'stress_type', 'severity', 'affected_area_hectares',
            'description', 'evidence_count', 'is_verified', 'verification_notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_evidence_count(self, obj):
        """Get the number of vegetation indices used as evidence."""
        return obj.evidence_indices.count()


class AgriculturalStressEventCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating AgriculturalStressEvent instances."""
    
    class Meta:
        model = AgriculturalStressEvent
        fields = [
            'region', 'crop_mapping', 'detection_date', 'stress_type',
            'severity', 'affected_area_hectares', 'description',
            'geometry', 'evidence_indices'
        ]


class ConflictEventSerializer(GeoFeatureModelSerializer):
    """GeoJSON serializer for ConflictEvent model."""
    
    region_name = serializers.CharField(source='region.name', read_only=True)
    
    class Meta:
        model = ConflictEvent
        geo_field = 'location'
        fields = [
            'id', 'region', 'region_name', 'event_date', 'event_type',
            'description', 'source', 'intensity', 'affected_radius_km',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ConflictEventCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating ConflictEvent instances."""
    
    class Meta:
        model = ConflictEvent
        fields = [
            'region', 'event_date', 'event_type', 'description',
            'source', 'intensity', 'location', 'affected_radius_km'
        ]


class StressEventSummarySerializer(serializers.Serializer):
    """Serializer for stress event summary statistics."""
    
    total_events = serializers.IntegerField()
    events_by_type = serializers.DictField()
    events_by_severity = serializers.DictField()
    total_affected_area = serializers.FloatField()
    recent_events = AgriculturalStressEventSerializer(many=True)


class ConflictEventSummarySerializer(serializers.Serializer):
    """Serializer for conflict event summary statistics."""
    
    total_events = serializers.IntegerField()
    events_by_type = serializers.DictField()
    events_by_intensity = serializers.DictField()
    recent_events = ConflictEventSerializer(many=True)

