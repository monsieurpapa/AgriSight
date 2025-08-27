from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Agricultural Stress Events
    path('stress-events/', views.AgriculturalStressEventListCreateView.as_view(), name='stress-event-list-create'),
    path('stress-events/<uuid:pk>/', views.AgriculturalStressEventDetailView.as_view(), name='stress-event-detail'),
    path('stress-events/summary/', views.stress_event_summary, name='stress-event-summary'),
    
    # Conflict Events
    path('conflict-events/', views.ConflictEventListCreateView.as_view(), name='conflict-event-list-create'),
    path('conflict-events/<int:pk>/', views.ConflictEventDetailView.as_view(), name='conflict-event-detail'),
    path('conflict-events/summary/', views.conflict_event_summary, name='conflict-event-summary'),
]

