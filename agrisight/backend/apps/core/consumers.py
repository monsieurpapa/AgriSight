"""
WebSocket consumers for real-time updates.
"""

import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model
from django.core.cache import cache
from apps.geospatial.models import Region
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class AgriSightConsumer(AsyncWebsocketConsumer):
    """Main WebSocket consumer for AgriSight real-time updates."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.room_groups = set()
        self.authenticated = False

    async def connect(self):
        """Handle WebSocket connection."""
        self.room_name = "agrisight_updates"
        self.room_group_name = f"agrisight_{self.room_name}"

        # Use session-based auth if available via AuthMiddlewareStack
        self.user = self.scope.get('user')
        if self.user and getattr(self.user, 'is_authenticated', False):
            self.authenticated = True
        else:
            await self.close(code=4001)
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        logger.info(f"WebSocket connected: {self.channel_name}")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave all room groups
        for group in self.room_groups:
            await self.channel_layer.group_discard(
                group,
                self.channel_name
            )
        
        logger.info(f"WebSocket disconnected: {self.channel_name}, code: {close_code}")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'auth':
                await self.handle_auth(data)
            elif message_type == 'subscribe':
                await self.handle_subscribe(data)
            elif message_type == 'unsubscribe':
                await self.handle_unsubscribe(data)
            elif message_type == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")

    async def handle_auth(self, data):
        """Handle authentication."""
        token = data.get('token')
        if not token:
            await self.send(text_data=json.dumps({
                'type': 'auth_error',
                'message': 'No authentication token provided'
            }))
            return
        
        # Authenticate using session token
        user = await self.authenticate_user(token)
        if user:
            self.user = user
            self.authenticated = True
            await self.send(text_data=json.dumps({
                'type': 'auth_success',
                'user_id': str(user.id),
                'username': user.username
            }))
            logger.info(f"User authenticated: {user.username}")
        else:
            await self.send(text_data=json.dumps({
                'type': 'auth_error',
                'message': 'Invalid authentication token'
            }))

    async def handle_subscribe(self, data):
        """Handle subscription to specific channels."""
        if not self.authenticated:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Authentication required'
            }))
            return
        
        channel = data.get('channel')
        if channel not in ['region_updates', 'processing_updates', 'system_alerts']:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Unsupported channel'
            }))
            return
        group_name = f"agrisight_{channel}"
        
        # Add specific identifiers to group name
        if channel == 'region_updates' and data.get('region_id'):
            region_id = data.get('region_id')
            has_access = await self.user_has_region_access(region_id)
            if not has_access:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Access denied to region updates'
                }))
                return
            group_name += f"_{region_id}"
        elif channel == 'processing_updates' and data.get('task_id'):
            group_name += f"_{data['task_id']}"
        
        await self.channel_layer.group_add(
            group_name,
            self.channel_name
        )
        
        self.room_groups.add(group_name)
        
        await self.send(text_data=json.dumps({
            'type': 'subscription_success',
            'channel': channel,
            'group': group_name
        }))
        
        logger.info(f"Subscribed to {group_name}")

    async def handle_unsubscribe(self, data):
        """Handle unsubscription from specific channels."""
        channel = data.get('channel')
        group_name = f"agrisight_{channel}"
        
        # Add specific identifiers to group name
        if channel == 'region_updates' and data.get('region_id'):
            group_name += f"_{data['region_id']}"
        elif channel == 'processing_updates' and data.get('task_id'):
            group_name += f"_{data['task_id']}"
        
        if group_name in self.room_groups:
            await self.channel_layer.group_discard(
                group_name,
                self.channel_name
            )
            self.room_groups.remove(group_name)
            
            await self.send(text_data=json.dumps({
                'type': 'unsubscription_success',
                'channel': channel
            }))
            
            logger.info(f"Unsubscribed from {group_name}")

    @database_sync_to_async
    def authenticate_user(self, session_key):
        """Authenticate user using session key."""
        try:
            session = Session.objects.get(session_key=session_key)
            user_id = session.get_decoded().get('_auth_user_id')
            if user_id:
                return User.objects.get(id=user_id)
        except (Session.DoesNotExist, User.DoesNotExist):
            pass
        return None

    @database_sync_to_async
    def user_has_region_access(self, region_id):
        if not region_id:
            return False
        if self.user.user_type == 'admin':
            return Region.objects.filter(id=region_id).exists()
        if self.user.organization:
            return Region.objects.filter(id=region_id, organizations=self.user.organization).exists()
        return False

    # Message handlers for different types of updates
    async def stress_event_update(self, event):
        """Handle stress event updates."""
        await self.send(text_data=json.dumps({
            'type': 'stress_event',
            'payload': event['data']
        }))

    async def processing_update(self, event):
        """Handle processing task updates."""
        await self.send(text_data=json.dumps({
            'type': 'processing_update',
            'payload': event['data']
        }))

    async def system_alert(self, event):
        """Handle system alerts."""
        await self.send(text_data=json.dumps({
            'type': 'system_alert',
            'payload': event['data']
        }))

    async def vegetation_update(self, event):
        """Handle vegetation data updates."""
        await self.send(text_data=json.dumps({
            'type': 'vegetation_update',
            'payload': event['data']
        }))

    async def conflict_event_update(self, event):
        """Handle conflict event updates."""
        await self.send(text_data=json.dumps({
            'type': 'conflict_event',
            'payload': event['data']
        }))


class RegionUpdatesConsumer(AsyncWebsocketConsumer):
    """Consumer for region-specific updates."""
    
    async def connect(self):
        self.region_id = self.scope['url_route']['kwargs']['region_id']
        self.room_group_name = f'agrisight_region_{self.region_id}'
        self.user = self.scope.get('user')

        if not self.user or not getattr(self.user, 'is_authenticated', False):
            await self.close(code=4001)
            return

        has_access = await self.user_has_region_access(self.region_id)
        if not has_access:
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        
        # Broadcast to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'region_update',
                'data': data
            }
        )

    async def region_update(self, event):
        await self.send(text_data=json.dumps(event['data']))

    @database_sync_to_async
    def user_has_region_access(self, region_id):
        if self.user.user_type == 'admin':
            return Region.objects.filter(id=region_id).exists()
        if self.user.organization:
            return Region.objects.filter(id=region_id, organizations=self.user.organization).exists()
        return False
