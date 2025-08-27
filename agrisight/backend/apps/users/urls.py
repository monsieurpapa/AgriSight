from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.UserListCreateView.as_view(), name='user-list-create'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('me/', views.current_user, name='current-user'),
    path('me/update/', views.update_current_user, name='update-current-user'),
]

