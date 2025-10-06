"""
Permission system for AgriSight platform.
Defines role-based permissions and custom permission classes.
"""

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit objects.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Write permissions are only allowed to admins
        return request.user.is_authenticated and request.user.user_type == 'admin'


class IsAdminOrOrganizationMember(permissions.BasePermission):
    """
    Custom permission to allow admins or organization members to access data.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Admins have access to everything
        if request.user.user_type == 'admin':
            return True
        
        # Users must belong to an organization
        return request.user.organization is not None


class HasPermission(permissions.BasePermission):
    """
    Custom permission to check for specific permissions.
    """
    def __init__(self, required_permission):
        self.required_permission = required_permission

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Admins have all permissions
        if request.user.user_type == 'admin':
            return True
        
        # Check if user has the required permission
        return self._user_has_permission(request.user, self.required_permission)

    def _user_has_permission(self, user, permission):
        """
        Check if user has the specified permission based on their role.
        """
        role_permissions = {
            'admin': ['*'],  # All permissions
            'humanitarian': ['view_data', 'export_data', 'generate_reports', 'view_analytics'],
            'cooperative': ['view_data', 'view_analytics', 'manage_regions', 'view_stress_events'],
            'government': ['view_data', 'view_analytics', 'manage_organizations', 'view_all_regions'],
            'researcher': ['view_data', 'view_analytics', 'export_data', 'view_stress_events', 'view_conflict_events']
        }
        
        user_permissions = role_permissions.get(user.user_type, ['view_data'])
        return '*' in user_permissions or permission in user_permissions


class CanViewData(permissions.BasePermission):
    """
    Permission to view data - most basic permission.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated


class CanExportData(permissions.BasePermission):
    """
    Permission to export data.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.user_type == 'admin':
            return True
        
        return request.user.user_type in ['humanitarian', 'researcher']


class CanManageRegions(permissions.BasePermission):
    """
    Permission to manage regions.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.user_type == 'admin':
            return True
        
        return request.user.user_type in ['cooperative', 'government']


class CanManageOrganizations(permissions.BasePermission):
    """
    Permission to manage organizations.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.user_type in ['admin', 'government']


class CanViewStressEvents(permissions.BasePermission):
    """
    Permission to view stress events.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.user_type == 'admin':
            return True
        
        return request.user.user_type in ['cooperative', 'researcher']


class CanViewConflictEvents(permissions.BasePermission):
    """
    Permission to view conflict events.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.user_type == 'admin':
            return True
        
        return request.user.user_type in ['humanitarian', 'researcher', 'government']


class CanGenerateReports(permissions.BasePermission):
    """
    Permission to generate reports.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.user_type == 'admin':
            return True
        
        return request.user.user_type in ['humanitarian', 'researcher']


class CanViewAnalytics(permissions.BasePermission):
    """
    Permission to view analytics.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # All authenticated users can view analytics
        return True


class CanViewAllRegions(permissions.BasePermission):
    """
    Permission to view all regions (not just organization's regions).
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.user_type in ['admin', 'government']


def get_user_permissions(user):
    """
    Get all permissions for a user based on their role.
    """
    if not user.is_authenticated:
        return []
    
    role_permissions = {
        'admin': ['*'],  # All permissions
        'humanitarian': ['view_data', 'export_data', 'generate_reports', 'view_analytics'],
        'cooperative': ['view_data', 'view_analytics', 'manage_regions', 'view_stress_events'],
        'government': ['view_data', 'view_analytics', 'manage_organizations', 'view_all_regions'],
        'researcher': ['view_data', 'view_analytics', 'export_data', 'view_stress_events', 'view_conflict_events']
    }
    
    return role_permissions.get(user.user_type, ['view_data'])


def user_has_permission(user, permission):
    """
    Check if a user has a specific permission.
    """
    if not user.is_authenticated:
        return False
    
    permissions = get_user_permissions(user)
    return '*' in permissions or permission in permissions
