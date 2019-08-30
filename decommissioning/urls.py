from django.conf.urls import url

from django.urls import path

from . import views

app_name = 'decommissioning'

urlpatterns = [
    # ex: /decommissioning/
    path('', views.decommissioning, name='decommissioning'),
]