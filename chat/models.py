from django.db import models
from django.conf import settings
from django.utils import timezone


class Conversation(models.Model):
    """
    A conversation between two users.
    """
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Conversation between " + ", ".join([user.username for user in self.participants.all()])

    def latest_message(self):
        return self.messages.order_by('-timestamp').first()


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, related_name="messages", on_delete=models.CASCADE, null=True)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)  # Ensure default=False
    def __str__(self):
        return f"{self.sender.username}: {self.content[:20]}"
