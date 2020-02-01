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

        # data verwijderen - CertServerSSLVirtualServer tabel
        CertServerSSLVirtualServer.objects.all().delete()

        #verzameltabel CertClientSSLVirtualServer opbouwen waarmee de certificaten op verloopdatum kunnen worden gesorteerd.
        #
        #zowel de vitual server als de client ssl profielen kunnen vaker zijn toegepast per certificaat.
        #
        #cert_name = cert_from_db_app.full_name
        #cert_partition = cert_from_db_app.partition
        #cert_expiration = cert_from_db_app.expiration
        #cert_cluster = BigIPNodes.objects.get(pk=cert_from_db_app.bigip_name_id)
        #cssl_name = cssl_from_db_app.full_name
        #cssl_partition = cssl_from_db_app.partition
        #vs_name = vs_from_db_app.full_name
        #vs_partition = vs_from_db_app.partition
        #vs_ip =  vs_from_db_app.destination
        #

        for cert_from_db_app in Certificates.objects.all():

            #print('cert name: ' + cert_from_db_app.full_name)

            #maak per client ssl profiel een certvs entry in de CertClientSSLVirtualServer tabel
            for cssl_from_db_app in ProfileSSLClient.objects.filter(certificates__full_name__exact=cert_from_db_app.full_name,
                                                                    bigip_name_id__exact=cert_from_db_app.bigip_name_id):

                #print('cssl name: ' + cssl_from_db_app.full_name)

                #en breidt dit uit met virtual server configuratie informatie
                for vs_from_db_app in VirtualServer.objects.filter(profile_client_ssl__full_name=cssl_from_db_app.full_name,
                                                                   bigip_name_id__exact=cssl_from_db_app.bigip_name_id):

                    #print('virtual server name: ' + vs_from_db_app.full_name)
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

            # verzameltabel CertServerSSLVirtualServer opbouwen waarmee de certificaten op verloopdatum kunnen worden gesorteerd.
            #
            # zowel de vitual server als de Server ssl profielen kunnen vaker zijn toegepast per certificaat.
            #
            # cert_name = cert_from_db_app.full_name
            # cert_partition = cert_from_db_app.partition
            # cert_expiration = cert_from_db_app.expiration
            # cert_cluster = BigIPNodes.objects.get(pk=cert_from_db_app.bigip_name_id)
            # server_ssl_name = cssl_from_db_app.full_name
            # server_ssl_partition = cssl_from_db_app.partition
            # vs_name = vs_from_db_app.full_name
            # vs_partition = vs_from_db_app.partition
            # vs_ip =  vs_from_db_app.destination
            #

            # haal de server ssl profielen op voor het huidige certificaat.
            # als het certificaat niet wordt gebruikt in de SSL server tabel, ga dan door met het volgende cert.

            if ProfileSSLServer.objects.filter(certificate_id__exact=cert_from_db_app.id).exists():
                #print(ProfileSSLServer.objects.filter(certificate_id__exact=cert_from_db_app.id).values())

                for server_ssl_from_db_app in ProfileSSLServer.objects.filter(certificate_id__exact=cert_from_db_app.id,
                                                                              bigip_name_id__exact=cert_from_db_app.bigip_name_id):

                    #print('server ssl name: ' + server_ssl_from_db_app.full_name)

                    # en breidt dit uit met virtual server configuratie informatie
                    for vs_from_db_app in VirtualServer.objects.filter(profile_server_ssl__full_name=server_ssl_from_db_app.full_name,
                                                                       bigip_name_id__exact=server_ssl_from_db_app.bigip_name_id):

                        #print('virtual server name: ' + vs_from_db_app.full_name)

                        # voeg een nieuwe certificaatregel toe per virtual server in de CertClientSSLVirtualServer tabel
                        cert_servertssl_virtualserver = CertServerSSLVirtualServer(
                            cert_name=cert_from_db_app.full_name,
                            cert_partition=cert_from_db_app.partition,
                            cert_expiration=cert_from_db_app.expiration,
                            cert_cluster=BigIPNodes.objects.get(pk=cert_from_db_app.bigip_name_id),
                            server_ssl_name=server_ssl_from_db_app.full_name,
                            server_ssl_partition=server_ssl_from_db_app.partition,
                            vs_name=vs_from_db_app.full_name,
                            vs_partition=vs_from_db_app.partition,
                            vs_ip=vs_from_db_app.destination)

                        cert_servertssl_virtualserver.save()

            else:
                continue


        context = {"cert_clientssl_virtualserver": CertClientSSLVirtualServer.objects.all(),
                   'cert_serverssl_virtualserver': CertServerSSLVirtualServer.objects.all()}


    return render(request, 'certificates/certificates.html', context)