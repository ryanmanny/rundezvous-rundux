from django.urls import path

from chat import views


urlpatterns = [
    path('chatroom', views.chatroom, name='chatroom'),
    path('chatroom/new_messages/<int:last_message_id>', views.new_messages, name='new_messages'),

    path('message', views.message, name='post_message'),
    path('message/<int:message_id>', views.message, name='get_message'),
]
