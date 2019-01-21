from django.urls import path

from chat import views


urlpatterns = [
    path('chatroom/<int:room_id>', views.chatroom, name='chatroom'),
]
