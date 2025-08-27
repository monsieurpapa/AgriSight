from django.urls import path
from . import views

app_name = 'organizations'

urlpatterns = [
    # Subscription plans
    path('subscription-plans/', views.SubscriptionPlanListView.as_view(), name='subscription-plan-list'),
    path('subscription-plans/<int:pk>/', views.SubscriptionPlanDetailView.as_view(), name='subscription-plan-detail'),
    
    # Organizations
    path('', views.OrganizationListCreateView.as_view(), name='organization-list-create'),
    path('<int:pk>/', views.OrganizationDetailView.as_view(), name='organization-detail'),
    path('current/', views.current_organization, name='current-organization'),
]

