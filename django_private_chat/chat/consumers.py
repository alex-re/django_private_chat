# A async-chat-consumers with first method(DJANGO_ALLOW_ASYNC_UNSAFE=True)

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import Dialog, Message
from django.db.models import Q


class ChatConsumer(AsyncWebsocketConsumer):
    async def new_message(self, data):
        sender = data['from']
        # if sender != self.scope['user'].username: return HttpResponse('Send message from your self!')
        sender_user = await self.get_user_by_username(username=sender)
        opponent_user = await self.get_user_by_username(username=self.scope['url_route']['kwargs']['room_name'])
        dialog = await self.get_dialog_by_users(user1=self.scope['user'], user2=opponent_user)
        serialized_message = await self.create_message(sender=sender_user, text=data['message'], dialog=dialog)
        content = {
            'command': 'new_message',
            'message': message
        }
        return await self.send_chat_message(serialized_message)


    async def fetch_messages(self, data):
        opponent_user = await self.get_user_by_username(username=self.room_name)
        dialog = await self.get_dialog_by_users(user1=self.scope['user'], user2=opponent_user)
        serialized_messages = await self.get_messages_by_dialog(dialog=dialog)
        content = {
            'command': 'messages',
            'messages': serialized_messages
        }
        await self.send_message(content)

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message
    }

    async def connect(self):
        # self.room_name = self.scope['url_route']['kwargs']['room_name']
        opponent_user = await self.get_user_by_username(username=self.scope['url_route']['kwargs']['room_name'])
        dialog = await self.get_dialog_by_users(user1=self.scope['user'], user2=opponent_user)

        self.room_name = dialog.owner.username
        self.room_group_name = 'chat_%s' % self.room_name
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.commands[data['command']](self, data)

    async def send_chat_message(self, message):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def send_message(self, message):
        await self.send(text_data=json.dumps(message))

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))
        # await self.send(text_data=json.dumps({
        #     'message': message
        # }))

    @database_sync_to_async
    def get_user_by_username(self, username):
        return get_object_or_404(User, username=username)

    @database_sync_to_async
    def get_dialog_by_users(self, user1, user2):
        return Dialog.objects.filter(Q(owner=user1, opponent=user2) | Q(opponent=user1, owner=user2)).first()

    @database_sync_to_async
    def get_messages_by_dialog(self, dialog):
        messages = Message.objects.filter(dialog=dialog).order_by('timestamp').all()[:10]
        result = []
        for message in messages:
            result.append({
                'sender': message.sender.username,
                'content': message.text,
                'timestamp': str(message.timestamp)
            })
        return result

    @database_sync_to_async
    def create_message(self, sender, text, dialog):
        message = Message.objects.create(sender=sender, text=text, dialog=dialog)
        # Or we can send parameters to return from args given.
        return {'sender': message.sender.username,
            'content': message.text,
            'timestamp': str(message.timestamp)}
