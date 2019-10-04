from django.shortcuts import render
from datetime import datetime

from .models import BigIPNodes, Certificates, ProfileSSLClient, Database, VirtualServer

import requests

# Create your views here.

def database(request):

    # headers voor de API calls
    headers = {'Authorization': 'Basic YWRtaW46YWRtaW4=', 'Content-Type': 'application/json'}

    # bigip_node_list voor het weergeven van het form in database.html daarnaast wordt de database tabel meegegeven
    # voor het weergeven van datetimestamp
    bigip_node_list = BigIPNodes.objects.all()
    database = Database.objects.all()
    context = {'bigip_node_list': bigip_node_list, 'database':database}

    if 'update_db' in request.POST:

        ########### Database opschonen

        # omdat er geen timestamp beschikbaar is van de laatste config wijziging binnen het F5 cluster
        # kan er niet worden bepaald of bepaalde tabellen moeten worden bijgewerkt.
        # Daarom worden alle configuratietabellen die horen bij het betreffende F5 cluster opnieuw opgebouwd.

        # verwijderen huidige tabel data voor de betreffende BigIP node
        # queryset maken van alle data wat hoort bij de betreffende BigIP node
        # achterhalen van het pkid van de BigIP node waarvoor een update wordt gevraagd

        bigip_node_id = BigIPNodes.objects.get(bigip_ip__exact=request.POST['bigip_ip']).id

        # data verwijderen - certificates tabel
        Certificates.objects.all().filter(bigip_name_id__exact=bigip_node_id).delete()

        # data verwijderen - profileCSSLClient tabel
        ProfileSSLClient.objects.all().filter(bigip_name_id__exact=bigip_node_id).delete()

        # data verwijderen - virtualserver tabel
        VirtualServer.objects.all().filter(bigip_name_id__exact=bigip_node_id).delete()

        # data verwijderen - database tabel
        Database.objects.all().filter(bigip_name_id__exact=bigip_node_id).delete()

        # nieuwe database entries opnemen in een dictionary voor weergave op de database.html pagina
        database_updates = {}

        ########### REST API calls

        # certificaat details ophalen uit de opgegeven BigIP node
        bigip_ip = request.POST['bigip_ip']
        url = 'https://%s/mgmt/tm/sys/crypto/cert' % bigip_ip
        certs = requests.get(url, headers=headers, verify=False)
        certs_list_dict = certs.json()['items']

        # client SSL profile details ophalen uit de opgegeven BigIP node
        bigip_ip = request.POST['bigip_ip']
        url = 'https://%s/mgmt/tm/ltm/profile/client-ssl' % bigip_ip
        profile_cssl = requests.get(url, headers=headers, verify=False)
        profile_cssl_list_dict = profile_cssl.json()['items']

        # virtual server details ophalen uit de opgegeven BigIP node
        # bij het wegschrijven naar de database worden ook nog API calls gedaan voor het achterhalen van de profielen
        bigip_ip = request.POST['bigip_ip']
        url = 'https://%s/mgmt/tm/ltm/virtual' % bigip_ip
        virtual_servers = requests.get(url, headers=headers, verify=False)
        virtual_servers_list_dict = virtual_servers.json()['items']

        ########### Database bijwerken

        #update op basis van deze queryset
        BigIPNode = BigIPNodes.objects.get(bigip_ip=bigip_ip)

        # certificaattabel
        new_certs = []
        for cert_dict in certs_list_dict:

            print(cert_dict)

            #bigip_name = BigIPNodes.objects.get(bigip_ip=bigip_ip)
            #name = cert_name form cert_dict['name'].split("/")
            #full_name = cert_dict['name']
            #partition = cert_partition cert_dict['name'].split("/")
            #expiration = cert_dict['apiRawValues']['expiration']
            #commonName = cert_dict['commonName']
            #certificateKeySize = cert_dict['apiRawValues']['certificateKeySize']
            #publicKeyType = cert_dict['apiRawValues']['publicKeyType']
            #organization = cert_dict['commonName']
            #ou = cert_dict['ou']
            #city = cert_dict['city']
            #country = cert_dict['country']
            #state = cert_dict['state']
            #subjectAlternativeName = cert_dict['subjectAlternativeName']

            slash, cert_partition, cert_name = cert_dict['name'].split("/")

            #kwargs = {'name': 'Adam')

            #func(kwargs['name'] if 'name' in kwargs.keys() else '')  # Expected Output: 'Adam'
            #func(kwargs['notakey'] if 'notakey' in kwargs.keys() else '')  # Expected Output: ''

            BigIPNode.certificates_set.create(bigip_name = BigIPNodes.objects.get(bigip_ip=bigip_ip),
                                              name=cert_name,
                                              full_name=cert_dict['name'],
                                              partition=cert_partition,
                                              expiration=datetime.strptime(cert_dict['apiRawValues']['expiration'],
                                                                           '%b %d %H:%M:%S %Y %Z'),
                                              commonName = cert_dict['commonName'],
                                              certificateKeySize = cert_dict['apiRawValues']['certificateKeySize'],
                                              publicKeyType = cert_dict['apiRawValues']['publicKeyType'],
                                              organization = cert_dict['commonName'] if 'organization' in cert_dict.keys() else '',
                                              ou = cert_dict['ou'] if 'ou' in cert_dict.keys() else '',
                                              city = cert_dict['city'] if 'city' in cert_dict.keys() else '',
                                              country = cert_dict['country'] if 'country' in cert_dict.keys() else '',
                                              state = cert_dict['state'] if 'state' in cert_dict.keys() else '',
                                              subjectAlternativeName=cert_dict['subjectAlternativeName'] if 'subjectAlternativeName' in cert_dict.keys() else ''
                                                  )

            new_certs.append(cert_dict['name'])

        # client SSL tabel
        new_profile_cssl = []
        for profile_cssl_dict in profile_cssl_list_dict:

            # bigip_name = BigIPNodes.objects.get(bigip_ip=bigip_ip)
            # certificate_id = Certificates.objects.get(full_name__exact=profile_cssl_dict['fullPath']).id
            # full_name = profile_cssl_dict['fullPath']
            # partition = profile_cssl_dict['partition']
            # name = profile_cssl_dict['name']

            #print(profile_cssl_dict['cert'])

            certificate_id = Certificates.objects.get(full_name__exact=profile_cssl_dict['cert'],
                                                      bigip_name_id__exact=bigip_node_id).id
            #print(certificate_id)
            BigIPNode.profilesslclient_set.create(certificate_id=certificate_id,
                                                  full_name=profile_cssl_dict['fullPath'],
                                                  partition=profile_cssl_dict['partition'],
                                                  name=profile_cssl_dict['name'])

            new_profile_cssl.append(profile_cssl_dict['name'])


        # virtual server tabel
        new_virtual_server = []

        for virtual_servers_dict in virtual_servers_list_dict:
            # bigip_name = BigIPNodes.objects.get(bigip_ip=bigip_ip)
            # profilesslclient_id = profilesslclient.objects.get(name__exact=profiles_dict['name']).id
            # full_name = virtual_servers_dict['fullPath']
            # partition = virtual_servers_dict['partition']
            # name = virtual_servers_dict['name']
            # destination = virtual_servers_dict['destination']

            # virtual server profile reference dictionary aanmaken
            profile_reference = virtual_servers_dict.get('profilesReference')
            profile_link_localhost = profile_reference.get('link')
            profile_link_bigip_ip = profile_link_localhost.replace('localhost', bigip_ip)

            # API call: create list of dictionaries of profiles which are assigned to virtual servers
            profiles = requests.get(profile_link_bigip_ip, headers=headers, verify=False)
            profiles_list_dict = profiles.json()['items']

            # virtual servers met SSL client profiel toevoegen
            # find client SSL profile in client SSL profile table and return PKID
            # iterate over ProfileSSLClient names
            for profilesslclient_name in ProfileSSLClient.objects.filter(bigip_name_id__exact=bigip_node_id).values_list('name', flat=True):

                #per naam controleren of deze of deze voorkomt in een profiel van de virtual server
                for profiles_dict in profiles_list_dict:

                    if profiles_dict['name'] == profilesslclient_name:
                        # SSL profiel gevonden -> tabel entry aanmaken
                        #print(profiles_dict['name'])
                        #print(ProfileSSLClient.objects.get(name__exact=profiles_dict['name']).id)
                        slash, virtual_server_partition, virtual_server_ip = virtual_servers_dict['destination'].split("/")
                        BigIPNode.virtualserver_set.create(full_name=virtual_servers_dict['fullPath'],
                                                           name=virtual_servers_dict['name'],
                                                           partition=virtual_servers_dict['partition'],
                                                           destination = virtual_server_ip,
                                                           profilesslclient_id = ProfileSSLClient.objects.get(name__exact=profiles_dict['name'],
                                                                                                              bigip_name_id__exact=bigip_node_id).id,
                                                           )
                        new_virtual_server.append(virtual_servers_dict['name'])
                    else:
                        continue




        # toegevoegde entries meegeven om weer te geven op de database.html pagina
        database_updates['certificates'] = new_certs
        database_updates['profile_cssl'] = new_profile_cssl
        database_updates['virtual_servers'] = new_virtual_server

        # database tabel bijwerken zodat het duidelijk is van welke datum de huidige configuratie is
        #bigip_name_id = BigIPNodes.objects.get(full_name__exact=).id
        BigIPNode.database_set.create()

        context = {'database_updates' : database_updates}

    return render(request, 'database/database.html', context)