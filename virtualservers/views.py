from django.shortcuts import render

from database.models import *
from .models import *

def virtualservers(request):

    print(request.POST)

    context = {}

    if 'update_vs_tables' in request.POST:

        ########### Database van de virtualserver app eerst opschonen

        # omdat er geen timestamp beschikbaar is van de laatste configwijziging binnen het F5 cluster
        # kan er niet worden bepaald of bepaalde tabellen moeten worden bijgewerkt.
        # Daarom worden alle configuratietabellen die horen bij het betreffende F5 cluster opnieuw opgebouwd.

        # data verwijderen - VirtualServer tabel
        VirtualServerVerzamel.objects.all().delete()

        # virtualserver tabel doorlopen uit de DB app en de virtualserverclustertabel vullen
        for vs_from_db_app in VirtualServer.objects.all():

            # verzameltabel virtualserverclustertabel opbouwen.
            #
            # vs_name = vs_from_db_app.full_name
            # vs_ip = vs_from_db_app.destination
            # vs_cluster = BigIPNodes.objects.get(pk=vs_from_db_app.bigip_name_id)
            # vs_irule = [irule.full_name for irule in vs_from_db_app.irule.all()]

            virtualserver_verzamel = VirtualServerVerzamel(vs_name = vs_from_db_app.full_name,
                                                        vs_ip = vs_from_db_app.destination,
                                                        vs_cluster = BigIPNodes.objects.get(pk=vs_from_db_app.bigip_name_id),
                                                        vs_irule = ", ".join([irule.full_name for irule in vs_from_db_app.irule.all()]))

            virtualserver_verzamel.save()

        context = {'database': Database.objects.all()}

    elif 'query_db_vs' in request.POST:

        context = {"virtualservers": VirtualServerVerzamel.objects.all()}

    return render(request, 'virtualservers/virtualservers.html', context)