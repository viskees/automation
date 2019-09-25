from django.conf.urls import url

from django.urls import path

from . import views

app_name = 'database'

urlpatterns = [
    # ex: /database/
    path('', views.database, name='database'),
]