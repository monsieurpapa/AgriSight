from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from apps.authentication.permissions import (
    CanViewData, CanManageRegions, CanViewAllRegions, CanManageOrganizations,
    user_has_permission
)
from .models import Region, RegionAccess, SatelliteImage, VegetationIndex, Crop, CropMapping
from .serializers import (
    RegionSerializer, RegionAccessSerializer, SatelliteImageSerializer,
    VegetationIndexSerializer, CropSerializer, CropMappingSerializer,
    CropMappingCreateSerializer
)


class RegionListCreateView(generics.ListCreateAPIView):
    """List all accessible regions or create a new region."""
    
    serializer_class = RegionSerializer
    permission_classes = [CanViewData]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['country', 'province']
    
    def get_queryset(self):
        # Users can only see regions their organization has access to
        user = self.request.user
        if user.user_type == 'admin' or user_has_permission(user, 'view_all_regions'):
            return Region.objects.all()
        elif user.organization:
            return Region.objects.filter(organizations=user.organization)
        else:
            return Region.objects.none()
    
    def perform_create(self, serializer):
        # Only users with manage_regions permission can create regions
        if not user_has_permission(self.request.user, 'manage_regions'):
            raise permissions.PermissionDenied("You don't have permission to create regions.")
        serializer.save()


class RegionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a region."""
    
    serializer_class = RegionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'admin':
            return Region.objects.all()
        elif user.organization:
            return Region.objects.filter(organizations=user.organization)
        else:
            return Region.objects.none()


class RegionAccessListCreateView(generics.ListCreateAPIView):
    """List all region access records or create a new one."""
    
    serializer_class = RegionAccessSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['organization', 'region', 'access_level']
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'admin':
            return RegionAccess.objects.all().select_related('organization', 'region')
        elif user.organization:
            return RegionAccess.objects.filter(organization=user.organization).select_related('organization', 'region')
        else:
            return RegionAccess.objects.none()


class SatelliteImageListCreateView(generics.ListCreateAPIView):
    """List all satellite images or create a new one."""
    
    serializer_class = SatelliteImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['region', 'satellite_name', 'is_processed']
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'admin':
            return SatelliteImage.objects.all().select_related('region')
        elif user.organization:
            accessible_regions = Region.objects.filter(organizations=user.organization)
            return SatelliteImage.objects.filter(region__in=accessible_regions).select_related('region')
        else:
            return SatelliteImage.objects.none()


class SatelliteImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a satellite image."""
    
    serializer_class = SatelliteImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'admin':
            return SatelliteImage.objects.all().select_related('region')
        elif user.organization:
            accessible_regions = Region.objects.filter(organizations=user.organization)
            return SatelliteImage.objects.filter(region__in=accessible_regions).select_related('region')
        else:
            return SatelliteImage.objects.none()


class VegetationIndexListCreateView(generics.ListCreateAPIView):
    """List all vegetation indices or create a new one."""
    
    serializer_class = VegetationIndexSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['index_type', 'satellite_image__region', 'satellite_image__satellite_name']
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'admin':
            return VegetationIndex.objects.all().select_related('satellite_image__region')
        elif user.organization:
            accessible_regions = Region.objects.filter(organizations=user.organization)
            return VegetationIndex.objects.filter(
                satellite_image__region__in=accessible_regions
            ).select_related('satellite_image__region')
        else:
            return VegetationIndex.objects.none()


class VegetationIndexDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a vegetation index."""
    
    serializer_class = VegetationIndexSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'admin':
            return VegetationIndex.objects.all().select_related('satellite_image__region')
        elif user.organization:
            accessible_regions = Region.objects.filter(organizations=user.organization)
            return VegetationIndex.objects.filter(
                satellite_image__region__in=accessible_regions
            ).select_related('satellite_image__region')
        else:
            return VegetationIndex.objects.none()


class CropListCreateView(generics.ListCreateAPIView):
    """List all crops or create a new crop."""
    
    queryset = Crop.objects.all()
    serializer_class = CropSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']


class CropDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a crop."""
    
    queryset = Crop.objects.all()
    serializer_class = CropSerializer
    permission_classes = [permissions.IsAuthenticated]


class CropMappingListCreateView(generics.ListCreateAPIView):
    """List all crop mappings or create a new one."""
    
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['region', 'crop', 'mapping_date']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CropMappingCreateSerializer
        return CropMappingSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'admin':
            return CropMapping.objects.all().select_related('region', 'crop')
        elif user.organization:
            accessible_regions = Region.objects.filter(organizations=user.organization)
            return CropMapping.objects.filter(region__in=accessible_regions).select_related('region', 'crop')
        else:
            return CropMapping.objects.none()


class CropMappingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a crop mapping."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CropMappingCreateSerializer
        return CropMappingSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'admin':
            return CropMapping.objects.all().select_related('region', 'crop')
        elif user.organization:
            accessible_regions = Region.objects.filter(organizations=user.organization)
            return CropMapping.objects.filter(region__in=accessible_regions).select_related('region', 'crop')
        else:
            return CropMapping.objects.none()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def regions_near_point(request):
    """Find regions near a given point (latitude, longitude)."""
    try:
        lat = float(request.GET.get('lat'))
        lng = float(request.GET.get('lng'))
        distance_km = float(request.GET.get('distance', 10))  # Default 10km
        
        point = Point(lng, lat, srid=4326)
        distance = Distance(km=distance_km)
        
        user = request.user
        if user.user_type == 'admin':
            regions = Region.objects.filter(geometry__distance_lte=(point, distance))
        elif user.organization:
            accessible_regions = Region.objects.filter(organizations=user.organization)
            regions = accessible_regions.filter(geometry__distance_lte=(point, distance))
        else:
            regions = Region.objects.none()
        
        serializer = RegionSerializer(regions, many=True)
        return Response(serializer.data)
    
    except (ValueError, TypeError):
        return Response({'error': 'Invalid coordinates or distance'}, status=400)

