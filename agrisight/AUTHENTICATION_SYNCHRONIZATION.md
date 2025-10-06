# AgriSight Authentication Synchronization Guide

## Overview

This document outlines the comprehensive authentication and authorization system for the AgriSight platform, ensuring complete synchronization between frontend and backend for all user types.

## User Types and Roles

### Backend User Types (Django Model)
```python
USER_TYPE_CHOICES = (
    ('admin', 'Administrator'),
    ('humanitarian', 'Humanitarian Organization'),
    ('cooperative', 'Agricultural Cooperative'),
    ('government', 'Government Agency'),
    ('researcher', 'Researcher'),
)
```

### Frontend User Type Handling
The frontend handles both `user_type` and `user_type_code` fields for backward compatibility:
```javascript
const hasRole = (role) => {
  if (!state.user) return false;
  return state.user.user_type === role || state.user.user_type_code === role;
};
```

## Permission System

### Permission Definitions

| Permission | Description | User Types |
|------------|-------------|------------|
| `view_data` | Basic data viewing access | All authenticated users |
| `view_analytics` | Access to analytics and charts | All authenticated users |
| `export_data` | Export data in various formats | humanitarian, researcher |
| `generate_reports` | Create custom reports | humanitarian, researcher |
| `manage_regions` | Create and manage regions | cooperative, government |
| `view_stress_events` | View agricultural stress events | cooperative, researcher |
| `view_conflict_events` | View conflict-related events | humanitarian, researcher, government |
| `manage_organizations` | Manage organizations and users | government |
| `view_all_regions` | View all regions (not just organization's) | government |
| `admin_access` | Full administrative access | admin |

### Role-Based Permission Matrix

```javascript
const rolePermissions = {
  'admin': ['*'], // All permissions
  'humanitarian': ['view_data', 'export_data', 'generate_reports', 'view_analytics'],
  'cooperative': ['view_data', 'view_analytics', 'manage_regions', 'view_stress_events'],
  'government': ['view_data', 'view_analytics', 'manage_organizations', 'view_all_regions'],
  'researcher': ['view_data', 'view_analytics', 'export_data', 'view_stress_events', 'view_conflict_events']
};
```

## Backend Implementation

### Custom Permission Classes

```python
# apps/authentication/permissions.py
class CanViewData(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

class CanExportData(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.user_type == 'admin':
            return True
        return request.user.user_type in ['humanitarian', 'researcher']
```

### User Serializer with Permissions

```python
class CustomUserDetailsSerializer(UserDetailsSerializer):
    permissions = serializers.SerializerMethodField()
    
    def get_permissions(self, obj):
        role_permissions = {
            'admin': ['*'],
            'humanitarian': ['view_data', 'export_data', 'generate_reports', 'view_analytics'],
            'cooperative': ['view_data', 'view_analytics', 'manage_regions', 'view_stress_events'],
            'government': ['view_data', 'view_analytics', 'manage_organizations', 'view_all_regions'],
            'researcher': ['view_data', 'view_analytics', 'export_data', 'view_stress_events', 'view_conflict_events']
        }
        return role_permissions.get(obj.user_type, ['view_data'])
```

### View-Level Permission Implementation

```python
class RegionListCreateView(generics.ListCreateAPIView):
    permission_classes = [CanViewData]
    
    def perform_create(self, serializer):
        if not user_has_permission(self.request.user, 'manage_regions'):
            raise permissions.PermissionDenied("You don't have permission to create regions.")
        serializer.save()
```

## Frontend Implementation

### AuthContext Permission System

```javascript
const hasPermission = (permission) => {
  if (!state.user) return false;
  
  // Admin has all permissions
  if (hasRole('admin')) return true;
  
  // Check user-specific permissions from backend
  if (state.user.permissions && state.user.permissions.includes(permission)) {
    return true;
  }
  
  // Check role-based permissions
  const userRole = state.user.user_type || state.user.user_type_code;
  const permissions = rolePermissions[userRole] || [];
  
  return permissions.includes('*') || permissions.includes(permission);
};
```

### Component-Level Permission Usage

```javascript
// In Sidebar component
const navigationItems = [
  {
    name: 'Reports',
    href: '/reports',
    permission: 'generate_reports',
  },
  {
    name: 'Exports',
    href: '/exports',
    permission: 'export_data',
  }
];

// Filter items based on permissions
const filteredItems = items.filter(item => {
  if (!item.permission) return true;
  return hasPermission(item.permission);
});
```

## Authentication Flow

### 1. User Registration
- User selects user type during registration
- Backend validates user type and assigns appropriate permissions
- Frontend receives user data with permissions array

### 2. User Login
- Session-based authentication with CSRF protection
- Backend returns user data including permissions
- Frontend stores user data in AuthContext

### 3. Permission Checking
- Frontend checks permissions before rendering UI elements
- Backend validates permissions on API endpoints
- Consistent permission logic between frontend and backend

## Data Access Control

### Organization-Based Access
```python
def get_queryset(self):
    user = self.request.user
    if user.user_type == 'admin' or user_has_permission(user, 'view_all_regions'):
        return Region.objects.all()
    elif user.organization:
        return Region.objects.filter(organizations=user.organization)
    else:
        return Region.objects.none()
```

### Region Access Levels
```python
class RegionAccess(models.Model):
    access_level = models.CharField(max_length=20, choices=(
        ('view', 'View Only'),
        ('analyze', 'Analysis Access'),
        ('full', 'Full Access'),
    ))
```

## Security Considerations

### 1. CSRF Protection
- All state-changing requests include CSRF tokens
- Frontend automatically handles CSRF token refresh

### 2. Session Security
- Secure session cookies with HttpOnly flag
- Session timeout configuration
- Secure cookie settings for production

### 3. Permission Validation
- Backend validates all permissions on every request
- Frontend permission checks are for UX only
- No sensitive operations rely solely on frontend permissions

## API Endpoints

### Authentication Endpoints
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/user/` - Get current user data
- `POST /api/auth/registration/` - User registration
- `POST /api/auth/password/change/` - Change password

### Permission-Aware Endpoints
- `GET /api/v1/regions/` - List regions (filtered by organization)
- `POST /api/v1/regions/` - Create region (requires manage_regions)
- `GET /api/v1/analytics/stress-events/` - List stress events (requires view_stress_events)
- `GET /api/v1/exports/` - Export data (requires export_data)

## Testing Authentication

### Backend Tests
```python
def test_user_permissions(self):
    user = User.objects.create_user(
        email='test@example.com',
        user_type='cooperative'
    )
    self.assertTrue(user_has_permission(user, 'view_data'))
    self.assertTrue(user_has_permission(user, 'manage_regions'))
    self.assertFalse(user_has_permission(user, 'export_data'))
```

### Frontend Tests
```javascript
test('user has correct permissions', () => {
  const user = { user_type: 'cooperative' };
  expect(hasPermission('view_data')).toBe(true);
  expect(hasPermission('manage_regions')).toBe(true);
  expect(hasPermission('export_data')).toBe(false);
});
```

## Migration Guide

### From Old System
1. Update frontend to use new permission system
2. Migrate existing user permissions
3. Update API endpoints to use new permission classes
4. Test all user types and permission combinations

### Database Changes
- No database schema changes required
- User model already supports user types
- Permissions are calculated dynamically

## Troubleshooting

### Common Issues

1. **Permission Denied Errors**
   - Check user type assignment
   - Verify permission definitions match between frontend and backend
   - Ensure user is properly authenticated

2. **UI Elements Not Showing**
   - Check hasPermission() calls in components
   - Verify permission names match exactly
   - Check user data includes permissions array

3. **API Access Issues**
   - Verify permission classes are applied to views
   - Check user organization membership
   - Ensure proper authentication headers

### Debug Tools

```javascript
// Frontend debugging
console.log('User:', user);
console.log('User Type:', getUserType());
console.log('Permissions:', user.permissions);
console.log('Has Export Permission:', hasPermission('export_data'));

// Backend debugging
print(f"User: {request.user}")
print(f"User Type: {request.user.user_type}")
print(f"Permissions: {get_user_permissions(request.user)}")
```

## Best Practices

1. **Always validate permissions on the backend**
2. **Use consistent permission names across frontend and backend**
3. **Test all user types and permission combinations**
4. **Document permission requirements for each feature**
5. **Use permission-based UI rendering for better UX**
6. **Implement proper error handling for permission denied scenarios**

## Future Enhancements

1. **Granular Permissions**: Add more specific permissions for fine-grained control
2. **Permission Groups**: Allow custom permission groups for organizations
3. **Temporary Permissions**: Time-limited permission grants
4. **Audit Logging**: Track permission usage and changes
5. **API Key Permissions**: Extend permission system to API keys

---

*This document should be updated whenever authentication or permission logic changes to maintain synchronization between frontend and backend.*
