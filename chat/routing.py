from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/chat/<str:room_name>/', consumers.ChatConsumer.as_asgi()),
    path('ws/private-chat/<int:conversation_id>/',
         consumers.PrivateChatConsumer.as_asgi()),
]
