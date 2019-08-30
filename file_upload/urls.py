from django.conf.urls import url

from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'file_upload'

urlpatterns = [
    # ex: /file_upload/
    path('', views.file_upload, name='file_upload'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)