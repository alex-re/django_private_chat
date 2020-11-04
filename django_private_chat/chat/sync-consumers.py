from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import Dialog, Message
from django.db.models import Q
from django.shortcuts import HttpResponse


class ChatConsumer(WebsocketConsumer):

    def fetch_messages(self, data):
        opponent_user = get_object_or_404(User, username=self.room_name)
        dialog = Dialog.objects.filter(Q(owner=self.scope['user'], opponent=opponent_user) | Q(opponent=self.scope['user'], owner=opponent_user)).first()

        messages = Message.objects.filter(dialog=dialog).order_by('timestamp').all()[:10]
        content = {
            'command': 'messages',
            'messages': self.messages_to_json(messages)
        }
        self.send_message(content)

    def new_message(self, data):
        sender = data['from']
        # if sender != self.scope['user'].username: return HttpResponse('Send message from your self!')
        sender_user = User.objects.filter(username=sender).first()  # get_object_or_404
        opponent_user = get_object_or_404(User, username=self.scope['url_route']['kwargs']['room_name'])
        dialog = Dialog.objects.filter(Q(owner=self.scope['user'], opponent=opponent_user) | Q(opponent=self.scope['user'], owner=opponent_user)).first()
        # print(self.room_name) username
        # print(self.room_group_name) 'chat_' + username
        message = Message.objects.create(
            sender=sender_user,
            text=data['message'],
            dialog_id=dialog.id)

        content = {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }
        return self.send_chat_message(content)

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self, message):
        return {
            'sender': message.sender.username,
            'content': message.text,
            'timestamp': str(message.timestamp)
        }

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message
    }

    def connect(self):
        # self.room_name = self.scope['url_route']['kwargs']['room_name']
        opponent_user = get_object_or_404(User, username=self.scope['url_route']['kwargs']['room_name'])
        dialog = Dialog.objects.filter(Q(owner=self.scope['user'], opponent=opponent_user) | Q(opponent=self.scope['user'], owner=opponent_user)).first()
        self.room_name = dialog.owner.username
        # print(self.room_name) <dialog owner username>
        self.room_group_name = 'chat_%s' % self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        # print(self.channel_name) specific.a71d1d2927e64093aa5c2f98acd58942!8dc0980d6ca84e4f9fef158a5f469be3
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        # self.commands[data['command']](self, data)
        # Checking if function exists.
        # if data['command'] in self.commands: self.commands[data['command']](self, data)
        command = data.get('command', None)
        if command == 'fetch_messages':
            self.fetch_messages(data)
        elif command == 'new_message':
            self.new_message(data)            

    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def send_message(self, message):
        self.send(text_data=json.dumps(message))
        # print(message) {'command': 'messages', 'messages': [{'sender': 'ali', 'content': 'g', 'timestamp': '2020-10-27 16:38:54.563293+00:00'}]}

    def chat_message(self, event):
        message = event['message']
        # print(event) {'type': 'chat_message', 'message': {'command': 'new_message', 'message': {'sender': 'ali', 'content': 'g', 'timestamp': '2020-10-27 16:38:54.563293+00:00'}}}
        # print(json.dumps(message)) {"command": "new_message", "message": {"sender": "ali", "content": "ff", "timestamp": "2020-10-27 16:36:03.707365+00:00"}}
        self.send(text_data=json.dumps(message))