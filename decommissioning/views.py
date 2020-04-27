from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from django.core.validators import validate_ipv4_address
from django.core.exceptions import ValidationError

from database.models import *
from .models import *

# Create your views here.


def decommissioning(request):
    print(request.POST)

    context = {}

    if 'update_decom_tables' in request.POST:

        # IrulesNotAssigned table
        # irule_name =
        # irule_cluster =


        # Deze query geeft de virtualservers waaraan een irule gekoppeld is
        vs_met_irule = VirtualServer.objects.filter(irule__isnull=False)

        # maak een lijst met irule pk ID's en pas deze toe op een irule queryset
        irules_assigned = []

        for vs in vs_met_irule:
            for irule in vs.irule.all():
                # print("virtual server: " + vs.full_name + "irule ID: " + str(irule.id))
                irules_assigned.append(irule.id)

        # Deze query geeft de irules die niet zijn toegekend aan virtual servers
        # Irule.objects.exclude(id__in=irules_assigned)

        for irule in Irule.objects.exclude(id__in=irules_assigned):

            irule_not_assigned = IrulesNotAssigned(irule_name = irule.full_name,
                                                   irule_cluster = BigIPNodes.objects.get(pk=irule.bigip_name_id)
            )

            irule_not_assigned.save()

        context = {'database': Database.objects.all()}


    elif 'search_by_ip' in request.POST:

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

        context = {"irules_niet_toegekend": IrulesNotAssigned.objects.all()}

    return render(request, 'decommissioning/decommissioning.html', context)