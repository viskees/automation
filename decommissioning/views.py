from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from django.core.validators import validate_ipv4_address
from django.core.exceptions import ValidationError

from database.models import *

# Create your views here.


def decommissioning(request):
    print(request.POST)

    context = {}

    if 'search_by_ip' in request.POST:

        context = {"search_by_ip": "search_by_ip" }

    elif 'vs_or_node_submit' in request.POST:

        print("Het opgegeven IP adres is: " + request.POST['ip_adres'])
        print("Het betreft een " + request.POST['vs_or_node'])

        # form data valideren
        try:
            validate_ipv4_address(request.POST['ip_adres'])
            print("IP is valid: " + request.POST['ip_adres'])
            valid_ip = request.POST['ip_adres']

        except ValidationError:
            print("opgegeven IP is niet valid")
            context = {'validation_error': 'validation_error'}


    elif 'query_db_irule' in request.POST:

        #Deze query geeft de irules weer die niet zijn toegekend aan virtual servers

        vs_met_irule = VirtualServer.objects.filter(irule__isnull=False)

        #maak een lijst met irule pk ID's en pas deze toe op een irule queryset

        for vs in vs_met_irule:
            for irule in vs.irule.all():
                print("virtual server: " + vs.full_name + "irule ID: " + str(irule.id))

        context = {"irules_niet_toegekend": Irule.objects.all()}

    return render(request, 'decommissioning/decommissioning.html', context)