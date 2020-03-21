from django.shortcuts import render

from database.models import *
from .models import *

from datetime import date

import requests

# Create your views here.

def certificates(request):

    print(request.POST)

    context = {}

    if 'update_cert_tables' in request.POST:

        ########### Database van de certificaten app eerst opschonen

        # omdat er geen timestamp beschikbaar is van de laatste configwijziging binnen het F5 cluster
        # kan er niet worden bepaald of bepaalde tabellen moeten worden bijgewerkt.
        # Daarom worden alle configuratietabellen die horen bij het betreffende F5 cluster opnieuw opgebouwd.

        # data verwijderen - CertClientSSLVirtualServer tabel
        CertClientSSLVirtualServer.objects.all().delete()

        # data verwijderen - CertServerSSLVirtualServer tabel
        CertServerSSLVirtualServer.objects.all().delete()

        # data verwijderen - CertServerSSLVirtualServerViaIruleAndDatagroup tabel
        CertServerSSLVirtualServerViaIruleAndDatagroup.objects.all().delete()

        for cert_from_db_app in Certificates.objects.all():

            #print('cert name: ' + cert_from_db_app.full_name)

            # verzameltabel CertClientSSLVirtualServer opbouwen waarmee de certificaten op verloopdatum kunnen worden gesorteerd.
            #
            # zowel de vitual server als de client ssl profielen kunnen vaker zijn toegepast per certificaat.
            #
            # cert_name = cert_from_db_app.full_name
            # cert_common_name = cert_from_db_app.commonname
            # cert_san = cert_from_db_app.subjectAlternativeName
            # cert_partition = cert_from_db_app.partition
            # cert_expiration = cert_from_db_app.expiration
            # cert_cluster = BigIPNodes.objects.get(pk=cert_from_db_app.bigip_name_id)
            # cssl_name = cssl_from_db_app.full_name
            # cssl_partition = cssl_from_db_app.partition
            # vs_name = vs_from_db_app.full_name
            # vs_partition = vs_from_db_app.partition
            # vs_ip =  vs_from_db_app.destination
            #
            for cssl_from_db_app in ProfileSSLClient.objects.filter(certificates__full_name__exact=cert_from_db_app.full_name,
                                                                    bigip_name_id__exact=cert_from_db_app.bigip_name_id):

                #print('cssl name: ' + cssl_from_db_app.full_name)

                #en breidt dit uit met virtual server configuratie informatie
                for vs_from_db_app in VirtualServer.objects.filter(profile_client_ssl__full_name=cssl_from_db_app.full_name,
                                                                   bigip_name_id__exact=cssl_from_db_app.bigip_name_id):

                    #print('virtual server name: ' + vs_from_db_app.full_name)
                    #voeg een nieuwe certificaatregel toe per virtual server in de CertClientSSLVirtualServer tabel
                    cert_clientssl_virtualserver = CertClientSSLVirtualServer(cert_name=cert_from_db_app.full_name,
                                                             cert_common_name=cert_from_db_app.commonName,
                                                             cert_san = cert_from_db_app.subjectAlternativeName,
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
            # cert_common_name = cert_from_db_app.commonname
            # cert_san = cert_from_db_app.subjectAlternativeName
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
                            cert_common_name = cert_from_db_app.commonName,
                            cert_san = cert_from_db_app.subjectAlternativeName,
                            cert_partition=cert_from_db_app.partition,
                            cert_expiration=cert_from_db_app.expiration,
                            cert_cluster=BigIPNodes.objects.get(pk=cert_from_db_app.bigip_name_id),
                            server_ssl_name=server_ssl_from_db_app.full_name,
                            server_ssl_partition=server_ssl_from_db_app.partition,
                            vs_name=vs_from_db_app.full_name,
                            vs_partition=vs_from_db_app.partition,
                            vs_ip=vs_from_db_app.destination)

                        cert_servertssl_virtualserver.save()


                    # certificaten die gekoppeld zijn aan een virtual server via irules/data groups worden toegevoegd
                    # aan tabel CertServerSSLVirtualServerViaIruleAndDatagroup

                    for datagroup_from_db_app in Datagroup.objects.filter(profile_server_ssl__full_name=server_ssl_from_db_app.full_name,
                                                                       bigip_name_id__exact=server_ssl_from_db_app.bigip_name_id):

                        print(server_ssl_from_db_app.full_name + ' gevonden voor datagroup ' + datagroup_from_db_app.full_name)

                        # op zoek naar irules waar deze datagroup aan naar verwijst

                        for irule_from_db_app in Irule.objects.filter(datagroup__full_name=datagroup_from_db_app.full_name,
                                                                   bigip_name_id__exact=datagroup_from_db_app.bigip_name_id):

                            print(datagroup_from_db_app.full_name + ' gevonden voor ' + irule_from_db_app.full_name)

                            # op zoek naar virtual servers waar deze irule naar verwijst

                            for vs_from_db_app in VirtualServer.objects.filter(irule__full_name=irule_from_db_app.full_name,
                                                                               bigip_name_id__exact=irule_from_db_app.bigip_name_id):

                                print(irule_from_db_app.full_name + ' gevonden voor virtual server ' + vs_from_db_app.full_name)

                                # voeg een nieuwe certificaatregel toe per virtual server
                                # in de CertServerSSLVirtualServerViaIruleAndDatagroup tabel
                                # cert_name = cert_from_db_app.full_name,
                                # cert_common_name = cert_from_db_app.commonname
                                # cert_san = cert_from_db_app.subjectAlternativeName
                                # cert_partition = cert_from_db_app.partition,
                                # cert_expiration = cert_from_db_app.expiration,
                                # cert_cluster = BigIPNodes.objects.get(pk=cert_from_db_app.bigip_name_id),
                                # server_ssl_name = server_ssl_from_db_app.full_name,
                                # server_ssl_partition = server_ssl_from_db_app.partition,
                                # irule_name =
                                # datagroup_name =
                                # vs_name = vs_from_db_app.full_name,
                                # vs_partition = vs_from_db_app.partition,
                                # vs_ip = vs_from_db_app.destination)

                                cert_irule_virtualserver = CertServerSSLVirtualServerViaIruleAndDatagroup(
                                    cert_name=cert_from_db_app.full_name,
                                    cert_common_name = cert_from_db_app.commonName,
                                    cert_san = cert_from_db_app.subjectAlternativeName,
                                    cert_partition=cert_from_db_app.partition,
                                    cert_expiration=cert_from_db_app.expiration,
                                    cert_cluster=BigIPNodes.objects.get(pk=cert_from_db_app.bigip_name_id),
                                    server_ssl_name=server_ssl_from_db_app.full_name,
                                    server_ssl_partition=server_ssl_from_db_app.partition,
                                    irule_name=irule_from_db_app.full_name,
                                    datagroup_name =datagroup_from_db_app.full_name,
                                    vs_name=vs_from_db_app.full_name,
                                    vs_partition=vs_from_db_app.partition,
                                    vs_ip=vs_from_db_app.destination)

                                cert_irule_virtualserver.save()


            else:
                continue

        context = {'database': Database.objects.all()}

    elif 'query_db_certs' in request.POST:

        context = {"cert_clientssl_virtualserver": CertClientSSLVirtualServer.objects.all(),
                   'cert_serverssl_virtualserver': CertServerSSLVirtualServer.objects.all(),
                   'cert_serverssl_datagroup_irule_virtualserver': CertServerSSLVirtualServerViaIruleAndDatagroup.objects.all()}


    return render(request, 'certificates/certificates.html', context)