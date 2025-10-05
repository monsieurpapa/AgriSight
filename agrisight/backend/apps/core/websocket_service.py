"""
WebSocket service for sending real-time updates.
"""

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger(__name__)


class WebSocketService:
    """Service for sending WebSocket messages."""
    
    def __init__(self):
        self.channel_layer = get_channel_layer()
    
    def send_stress_event_update(self, stress_event):
        """Send stress event update to WebSocket clients."""
        try:
            async_to_sync(self.channel_layer.group_send)(
                'agrisight_agrisight_updates',
                {
                    'type': 'stress_event_update',
                    'data': {
                        'id': str(stress_event.id),
                        'stress_type': stress_event.stress_type,
                        'severity': stress_event.severity,
                        'detection_date': stress_event.detection_date.isoformat(),
                        'region': {
                            'id': str(stress_event.region.id),
                            'name': stress_event.region.name
                        } if stress_event.region else None,
                        'affected_area_hectares': stress_event.affected_area_hectares,
                        'confidence_score': stress_event.confidence_score
                    }
                }
            )
            
            # Also send to region-specific group
            if stress_event.region:
                async_to_sync(self.channel_layer.group_send)(
                    f'agrisight_region_{stress_event.region.id}',
                    {
                        'type': 'stress_event_update',
                        'data': {
                            'id': str(stress_event.id),
                            'stress_type': stress_event.stress_type,
                            'severity': stress_event.severity,
                            'detection_date': stress_event.detection_date.isoformat(),
                            'region': {
                                'id': str(stress_event.region.id),
                                'name': stress_event.region.name
                            },
                            'affected_area_hectares': stress_event.affected_area_hectares,
                            'confidence_score': stress_event.confidence_score
                        }
                    }
                )
                
        except Exception as e:
            logger.error(f"Failed to send stress event update: {e}")
    
    def send_processing_update(self, task_id, status, progress=None, message=None):
        """Send processing task update to WebSocket clients."""
        try:
            async_to_sync(self.channel_layer.group_send)(
                'agrisight_agrisight_updates',
                {
                    'type': 'processing_update',
                    'data': {
                        'task_id': task_id,
                        'status': status,
                        'progress': progress,
                        'message': message,
                        'timestamp': None  # Will be set to current time
                    }
                }
            )
            
            # Also send to task-specific group
            async_to_sync(self.channel_layer.group_send)(
                f'agrisight_processing_updates_{task_id}',
                {
                    'type': 'processing_update',
                    'data': {
                        'task_id': task_id,
                        'status': status,
                        'progress': progress,
                        'message': message,
                        'timestamp': None  # Will be set to current time
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to send processing update: {e}")
    
    def send_system_alert(self, alert_type, message, severity='info', region_id=None):
        """Send system alert to WebSocket clients."""
        try:
            async_to_sync(self.channel_layer.group_send)(
                'agrisight_agrisight_updates',
                {
                    'type': 'system_alert',
                    'data': {
                        'id': f'alert_{alert_type}_{region_id or "global"}',
                        'type': alert_type,
                        'message': message,
                        'severity': severity,
                        'region_id': region_id,
                        'timestamp': None  # Will be set to current time
                    }
                }
            )
            
            # Also send to region-specific group if applicable
            if region_id:
                async_to_sync(self.channel_layer.group_send)(
                    f'agrisight_region_{region_id}',
                    {
                        'type': 'system_alert',
                        'data': {
                            'id': f'alert_{alert_type}_{region_id}',
                            'type': alert_type,
                            'message': message,
                            'severity': severity,
                            'region_id': region_id,
                            'timestamp': None  # Will be set to current time
                        }
                    }
                )
                
        except Exception as e:
            logger.error(f"Failed to send system alert: {e}")
    
    def send_vegetation_update(self, region_id, region_name, index_type, value, date):
        """Send vegetation data update to WebSocket clients."""
        try:
            async_to_sync(self.channel_layer.group_send)(
                'agrisight_agrisight_updates',
                {
                    'type': 'vegetation_update',
                    'data': {
                        'region_id': str(region_id),
                        'region_name': region_name,
                        'index_type': index_type,
                        'value': value,
                        'date': date.isoformat() if date else None,
                        'timestamp': None  # Will be set to current time
                    }
                }
            )
            
            # Also send to region-specific group
            async_to_sync(self.channel_layer.group_send)(
                f'agrisight_region_{region_id}',
                {
                    'type': 'vegetation_update',
                    'data': {
                        'region_id': str(region_id),
                        'region_name': region_name,
                        'index_type': index_type,
                        'value': value,
                        'date': date.isoformat() if date else None,
                        'timestamp': None  # Will be set to current time
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to send vegetation update: {e}")
    
    def send_conflict_event_update(self, conflict_event):
        """Send conflict event update to WebSocket clients."""
        try:
            async_to_sync(self.channel_layer.group_send)(
                'agrisight_agrisight_updates',
                {
                    'type': 'conflict_event_update',
                    'data': {
                        'id': str(conflict_event.id),
                        'event_type': conflict_event.event_type,
                        'intensity': conflict_event.intensity,
                        'event_date': conflict_event.event_date.isoformat(),
                        'region': {
                            'id': str(conflict_event.region.id),
                            'name': conflict_event.region.name
                        } if conflict_event.region else None,
                        'description': conflict_event.description,
                        'casualties': conflict_event.casualties,
                        'displaced_people': conflict_event.displaced_people
                    }
                }
            )
            
            # Also send to region-specific group
            if conflict_event.region:
                async_to_sync(self.channel_layer.group_send)(
                    f'agrisight_region_{conflict_event.region.id}',
                    {
                        'type': 'conflict_event_update',
                        'data': {
                            'id': str(conflict_event.id),
                            'event_type': conflict_event.event_type,
                            'intensity': conflict_event.intensity,
                            'event_date': conflict_event.event_date.isoformat(),
                            'region': {
                                'id': str(conflict_event.region.id),
                                'name': conflict_event.region.name
                            },
                            'description': conflict_event.description,
                            'casualties': conflict_event.casualties,
                            'displaced_people': conflict_event.displaced_people
                        }
                    }
                )
                
        except Exception as e:
            logger.error(f"Failed to send conflict event update: {e}")


# Global instance
websocket_service = WebSocketService()
