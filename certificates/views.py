from django.shortcuts import render

from database.models import *

import requests

# Create your views here.

def certificates(request):

    context = {}

    if 'query_db' in request.POST:
        #context = {"query_data": Certificates.objects.all().order_by('expiration')}
        context = {"query_data": VirtualServer.objects.select_related().order_by('profilesslclient__certificate__expiration')}

    return render(request, 'certificates/certificates.html', context)