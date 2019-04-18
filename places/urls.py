from django.urls import path

from places import views


urlpatterns = [
    path('test', views.geo_test, name='geo_test'),
    path('update_location', views.update_location, name='update_location'),
]
