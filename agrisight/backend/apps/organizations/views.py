from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Organization, SubscriptionPlan
from .serializers import (
    OrganizationSerializer, OrganizationCreateSerializer, OrganizationUpdateSerializer,
    SubscriptionPlanSerializer
)


class SubscriptionPlanListView(generics.ListAPIView):
    """List all active subscription plans."""
    
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.IsAuthenticated]


class SubscriptionPlanDetailView(generics.RetrieveAPIView):
    """Retrieve a specific subscription plan."""
    
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.IsAuthenticated]


class OrganizationListCreateView(generics.ListCreateAPIView):
    """List all organizations or create a new organization."""
    
    queryset = Organization.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['organization_type', 'subscription_plan', 'is_active']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrganizationCreateSerializer
        return OrganizationSerializer
    
    def get_queryset(self):
        # Admin users can see all organizations
        # Other users can only see their own organization
        user = self.request.user
        if user.user_type == 'admin':
            return Organization.objects.all().select_related('subscription_plan')
        elif user.organization:
            return Organization.objects.filter(id=user.organization.id).select_related('subscription_plan')
        else:
            return Organization.objects.none()


class OrganizationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an organization."""
    
    queryset = Organization.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return OrganizationUpdateSerializer
        return OrganizationSerializer
    
    def get_queryset(self):
        # Admin users can access all organizations
        # Other users can only access their own organization
        user = self.request.user
        if user.user_type == 'admin':
            return Organization.objects.all().select_related('subscription_plan')
        elif user.organization:
            return Organization.objects.filter(id=user.organization.id).select_related('subscription_plan')
        else:
            return Organization.objects.none()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_organization(request):
    """Get current user's organization information."""
    if request.user.organization:
        serializer = OrganizationSerializer(request.user.organization)
        return Response(serializer.data)
    else:
        return Response({'detail': 'User is not associated with any organization.'}, status=404)

