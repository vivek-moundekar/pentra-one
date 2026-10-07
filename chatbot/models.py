from django.db import models
from django.contrib.auth.models import User


class Conversation(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chat_conversations"
    )

    title = models.CharField(
        max_length=200,
        default="New Chat"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    class Meta:
        ordering = ["-updated_at"]


class Message(models.Model):

    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
    ]

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"

    class Meta:
        ordering = ["created_at"]