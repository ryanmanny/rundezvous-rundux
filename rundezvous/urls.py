from django.urls import path

from rundezvous import views


urlpatterns = [
    path('update_location', views.update_location, name='update-location'),
    path('location_required', views.location_required, name='location-required'),

    path('start', views.start, name='start-rundezvous'),
    path('router/', views.router, name='rundezvous-router'),

    path('waiting_room/', views.waiting_room, name='waiting-room'),
    path('active_rundezvous/', views.active_rundezvous, name='active-rundezvous'),
    path('review', views.review, name='review'),

    # CHAT STUFF
    path('chatroom', views.chatroom, name='chatroom'),
    path('chatroom/new_messages/<int:last_message_id>', views.new_messages, name='new-messages'),

    path('message', views.message, name='send_message'),
    path('message/<int:message_id>', views.message, name='get-message'),
]
