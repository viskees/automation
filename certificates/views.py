from django.shortcuts import render

from database.models import *
from .models import *

from datetime import date

import requests

# Create your views here.

def certificates(request):

    print(request.POST)

    context = {}

    if 'query_db_certs' in request.POST:

        ########### Database van de certificaten app eerst opschonen

        # omdat er geen timestamp beschikbaar is van de laatste configwijziging binnen het F5 cluster
        # kan er niet worden bepaald of bepaalde tabellen moeten worden bijgewerkt.
        # Daarom worden alle configuratietabellen die horen bij het betreffende F5 cluster opnieuw opgebouwd.

        # data verwijderen - CertClientSSLVirtualServer tabel
        CertClientSSLVirtualServer.objects.all().delete()

        #verzameltabel waarmee de certificaten op verloopdatum kunnen worden gesorteerd, bevat de volgende velden.
        #zowel de vitual server als de client ssl profielen kunnen vaker zijn toegepast per certificaat.
        #
        #cert_name =
        #cert_partition =
        #cert_expiration =
        #cert_cluster =
        #cssl_name =
        #cssl_partition =
        #vs_name =
        #vs_partition =
        #vs_ip =

        for cert_from_db_app in Certificates.objects.all():

            print('cert name: ' + cert_from_db_app.full_name)

            #maak per client ssl profiel een certvs entry in de CertClientSSLVirtualServer tabel
            for cssl_from_db_app in ProfileSSLClient.objects.filter(certificates__full_name__exact=cert_from_db_app.full_name):

                print('cssl name: ' + cssl_from_db_app.full_name)

                #en breidt dit uit met virtual server configuratie informatie
                for vs_from_db_app in VirtualServer.objects.filter(profilesslclient__full_name=cssl_from_db_app.full_name):

                    print('virtual server name: ' + vs_from_db_app.full_name)
                    #voeg een nieuwe certificaatregel toe per virtual server in de CertClientSSLVirtualServer tabel
                    cert_clientssl_virtualserver = CertClientSSLVirtualServer(cert_name=cert_from_db_app.full_name,
                                                             cert_partition=cert_from_db_app.partition,
                                                             cert_expiration=cert_from_db_app.expiration,
                                                             cert_cluster=BigIPNodes.objects.get(pk=cert_from_db_app.bigip_name_id),
                                                             cssl_name=cssl_from_db_app.full_name,
                                                             cssl_partition=cssl_from_db_app.partition,
                                                             vs_name=vs_from_db_app.full_name,
                                                             vs_partition=vs_from_db_app.partition,
                                                             vs_ip=vs_from_db_app.destination)

                    cert_clientssl_virtualserver.save()


        context = {"cert_clientssl_virtualserver": CertClientSSLVirtualServer.objects.all()}


    return render(request, 'certificates/certificates.html', context)