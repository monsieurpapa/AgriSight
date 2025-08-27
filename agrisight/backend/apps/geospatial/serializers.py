from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import Region, RegionAccess, SatelliteImage, VegetationIndex, Crop, CropMapping


class RegionSerializer(GeoFeatureModelSerializer):
    """GeoJSON serializer for Region model."""
    
    organization_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Region
        geo_field = 'geometry'
        fields = [
            'id', 'name', 'code', 'area_hectares', 'country', 'province',
            'organization_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'area_hectares', 'created_at', 'updated_at']
    
    def get_organization_count(self, obj):
        """Get the number of organizations with access to this region."""
        return obj.organizations.count()


class RegionAccessSerializer(serializers.ModelSerializer):
    """Serializer for RegionAccess model."""
    
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    region_name = serializers.CharField(source='region.name', read_only=True)
    
    class Meta:
        model = RegionAccess
        fields = [
            'id', 'organization', 'organization_name', 'region', 'region_name',
            'access_level', 'start_date', 'end_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SatelliteImageSerializer(serializers.ModelSerializer):
    """Serializer for SatelliteImage model."""
    
    region_name = serializers.CharField(source='region.name', read_only=True)
    vegetation_indices_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SatelliteImage
        fields = [
            'id', 'region', 'region_name', 'acquisition_date', 'satellite_name',
            'cloud_cover_percentage', 'resolution_meters', 'bands_available',
            'image_path', 'is_processed', 'processing_notes',
            'vegetation_indices_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_vegetation_indices_count(self, obj):
        """Get the number of vegetation indices calculated for this image."""
        return obj.vegetation_indices.count()


class VegetationIndexSerializer(serializers.ModelSerializer):
    """Serializer for VegetationIndex model."""
    
    satellite_image_info = serializers.SerializerMethodField()
    
    class Meta:
        model = VegetationIndex
        fields = [
            'id', 'satellite_image', 'satellite_image_info', 'index_type',
            'mean_value', 'min_value', 'max_value', 'std_deviation',
            'raster_path', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_satellite_image_info(self, obj):
        """Get basic info about the satellite image."""
        return {
            'satellite_name': obj.satellite_image.satellite_name,
            'acquisition_date': obj.satellite_image.acquisition_date,
            'region_name': obj.satellite_image.region.name
        }


class CropSerializer(serializers.ModelSerializer):
    """Serializer for Crop model."""
    
    mapping_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Crop
        fields = [
            'id', 'name', 'scientific_name', 'typical_growing_season',
            'optimal_ndvi_range', 'water_requirements', 'local_importance',
            'mapping_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_mapping_count(self, obj):
        """Get the number of mappings for this crop."""
        return obj.cropmapping_set.count()


class CropMappingSerializer(GeoFeatureModelSerializer):
    """GeoJSON serializer for CropMapping model."""
    
    crop_name = serializers.CharField(source='crop.name', read_only=True)
    region_name = serializers.CharField(source='region.name', read_only=True)
    
    class Meta:
        model = CropMapping
        geo_field = 'geometry'
        fields = [
            'id', 'region', 'region_name', 'crop', 'crop_name',
            'area_hectares', 'confidence_level', 'mapping_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CropMappingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating CropMapping instances."""
    
    class Meta:
        model = CropMapping
        fields = [
            'region', 'crop', 'area_hectares', 'confidence_level',
            'mapping_date', 'geometry'
        ]

