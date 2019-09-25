from django.conf.urls import url

from django.urls import path

from . import views

app_name = 'certificates'

urlpatterns = [
    # ex: /certificates/
    path('', views.certificates, name='certificates'),
]