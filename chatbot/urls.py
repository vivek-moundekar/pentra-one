from django.urls import path
from . import views

urlpatterns = [
    path("",views.chatbot,name="chatbot"),
    path("new/",views.new_chat,name="new_chat"),
    path("api/send/",views.send_message,name="send_message"),
    path("api/history/",views.chat_history,name="chat_history"),
    path("api/clear/",views.clear_chat,name="clear_chat"),
]