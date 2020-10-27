from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import Dialog, Message
from django.db.models import Q


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
        opponent_user = get_object_or_404(User, username=self.room_name)
        dialog = Dialog.objects.filter(Q(owner=self.scope['user'], opponent=opponent_user) | Q(opponent=self.scope['user'], owner=opponent_user)).first()
        message = Message.objects.create(
            sender=sender_user,
            text=data['message'],
            dialog=dialog)

        content = {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }
        return self.send_chat_message(content)

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
            # result.append({'author': message.author.username, 'content': message.content, 'timestamp': str(message.timestamp)})
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
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)  # If better check if function exists.
        

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

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))