from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
# from django.urls import re_path
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    # re_path('ws/pong/<str:room_name>/', consumers.PongConsumer.as_asgi()),
    path('ws/pong/<str:room_name>/', consumers.PongConsumer.as_asgi()),
]