from rest_framework import serializers
from .models import Organization, SubscriptionPlan


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer for SubscriptionPlan model."""
    
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'description', 'price_monthly', 'price_yearly',
            'max_users', 'max_regions', 'features', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for Organization model."""
    
    subscription_plan_details = SubscriptionPlanSerializer(source='subscription_plan', read_only=True)
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'organization_type', 'subscription_plan',
            'subscription_plan_details', 'is_active', 'contact_email',
            'contact_phone', 'address', 'user_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user_count']
    
    def get_user_count(self, obj):
        """Get the number of users in this organization."""
        return obj.user_set.count()


class OrganizationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new organizations."""
    
    class Meta:
        model = Organization
        fields = [
            'name', 'organization_type', 'subscription_plan',
            'contact_email', 'contact_phone', 'address'
        ]


class OrganizationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating organization information."""
    
    class Meta:
        model = Organization
        fields = [
            'name', 'organization_type', 'subscription_plan',
            'is_active', 'contact_email', 'contact_phone', 'address'
        ]

