from django.db import models
from django.contrib.auth.models import User


class Dialog(models.Model):
    owner = models.ForeignKey(User, related_name="selfDialogs", on_delete=models.CASCADE)
    opponent = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('owner', 'opponent')

    def __str__(self):
        return f'Dialog of {self.owner.username} with {self.opponent.username}'


class Message(models.Model):
    dialog = models.ForeignKey(Dialog, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name="messages", on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message of: {self.sender.username}'
