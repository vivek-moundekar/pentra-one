from django.contrib import admin

from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "title",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "user__username",
        "title",
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "conversation",
        "role",
        "created_at",
    )

    search_fields = (
        "content",
    )

    list_filter = (
        "role",
    )