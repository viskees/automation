from django.conf.urls import url

from django.urls import path

from . import views

app_name = 'certificates'

urlpatterns = [
    # ex: /file_upload/
    path('', views.certificates, name='certificates'),
]