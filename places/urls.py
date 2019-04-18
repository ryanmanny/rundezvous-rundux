from django.urls import path

from places import views


urlpatterns = [
    path('test', views.geo_test, name='geo_test'),
]
