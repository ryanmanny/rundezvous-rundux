from django.urls import path

from rundezvous import views


urlpatterns = [
    path('location_required', views.location_required, name='location_required'),

    path('rundezvous_router', views.rundezvous_router, name='rundezvous_router'),
    path('active_rundezvous', views.active_rundezvous, name='active_rundezvous'),

    # CHAT STUFF
    path('chatroom', views.chatroom, name='chatroom'),
    path('chatroom/new_messages/<int:last_message_id>', views.new_messages, name='new_messages'),

    path('message', views.message, name='send_message'),
    path('message/<int:message_id>', views.message, name='get_message'),
]
