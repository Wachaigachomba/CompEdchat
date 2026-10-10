import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Message, Conversation


class ChatConsumer(AsyncWebsocketConsumer):
    """
    A consumer for group chat (e.g., a 'general' chat room).
    """

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')
        username = self.scope['user'].username if self.scope['user'].is_authenticated else 'Anonymous'

        # Save the message to the database asynchronously
        await self.save_message(username, message)

        # Broadcast to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
            }
        )

    @sync_to_async
    def save_message(self, username, message):
        """
        Save a message to the database.
        Since this is a general chat, no conversation object is needed.
        """
        Message.objects.create(sender=self.scope['user'], content=message)

    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
        }))


class PrivateChatConsumer(AsyncWebsocketConsumer):
    """
    A consumer for private one-on-one chat.
    Expects a conversation ID in the URL.
    """

    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'private_chat_{self.conversation_id}'

        # Join conversation group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave conversation group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')
        username = self.scope['user'].username if self.scope['user'].is_authenticated else 'Anonymous'

        # Save the message to the database asynchronously
        await self.save_private_message(message)

        # Broadcast to conversation group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'private_chat_message',
                'message': message,
                'username': username,
            }
        )

    @sync_to_async
    def save_private_message(self, message):
        """
        Save a private message to the database.
        """
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            Message.objects.create(
                conversation=conversation, sender=self.scope['user'], content=message)
        except Conversation.DoesNotExist:
            pass  # Handle missing conversation case

    async def private_chat_message(self, event):
        message = event['message']
        username = event['username']
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
        }))
