from django.urls import path

from rundezvous import views


urlpatterns = [
    path('waiting_room', views.waiting_room, name='waiting_room'),
    path('active_rundezvous', views.active_rundezvous, name='active_rundezvous'),
]
