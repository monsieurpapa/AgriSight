"""
WebSocket routing configuration.
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/$', consumers.AgriSightConsumer.as_asgi()),
    re_path(r'ws/region/(?P<region_id>[0-9a-f-]+)/$', consumers.RegionUpdatesConsumer.as_asgi()),
]
