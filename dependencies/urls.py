from django.conf.urls import url

from django.urls import path

from . import views

app_name = 'dependencies'

urlpatterns = [
    # ex: /dependencies/
    path('', views.dependencies, name='dependencies'),
]