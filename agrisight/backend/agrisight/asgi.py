"""
ASGI config for AgriSight project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agrisight.settings')

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models. Everything
# below this line — including apps.core.routing, which pulls in consumers.py
# and its `from django.contrib.auth.models import AnonymousUser` — must come
# AFTER get_asgi_application() runs django.setup(), or it raises
# AppRegistryNotReady. (Previously unnoticed because nothing actually served
# agrisight.asgi:application; gunicorn ran the WSGI target instead.)
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from channels.auth import AuthMiddlewareStack  # noqa: E402
from apps.core.routing import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
