from django.urls import path

from chat import views


urlpatterns = [
    path('room/<room_id>', views.chatroom, name='chatroom'),
]
