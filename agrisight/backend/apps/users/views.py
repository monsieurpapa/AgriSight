from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer

User = get_user_model()


class UserListCreateView(generics.ListCreateAPIView):
    """List all users or create a new user."""
    
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer
    
    def get_queryset(self):
        # Filter users by organization for non-admin users
        user = self.request.user
        if user.user_type == 'admin':
            return User.objects.all().select_related('organization')
        elif user.organization:
            return User.objects.filter(organization=user.organization).select_related('organization')
        else:
            return User.objects.filter(id=user.id).select_related('organization')


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a user."""
    
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_queryset(self):
        # Filter users by organization for non-admin users
        user = self.request.user
        if user.user_type == 'admin':
            return User.objects.all().select_related('organization')
        elif user.organization:
            return User.objects.filter(organization=user.organization).select_related('organization')
        else:
            return User.objects.filter(id=user.id).select_related('organization')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_user(request):
    """Get current user information."""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_current_user(request):
    """Update current user information."""
    serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(UserSerializer(request.user).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

