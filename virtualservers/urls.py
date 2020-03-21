from django.conf.urls import url

from django.urls import path

from . import views

app_name = 'virtualservers'

urlpatterns = [
    # ex: /virtualservers/
    path('', views.virtualservers, name='virtualservers'),
]