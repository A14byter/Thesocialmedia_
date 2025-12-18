from django.urls import path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    path("ws/chats/<int:conv_id>/", ChatConsumer.as_asgi()),
]
