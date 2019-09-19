from django.contrib import admin

# Register your models here.
from .models import Certificates, BigIPNodes, Database, ProfileSSLClient

admin.site.register(Certificates)
admin.site.register(BigIPNodes)
admin.site.register(Database)
admin.site.register(ProfileSSLClient)