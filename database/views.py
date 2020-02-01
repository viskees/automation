from django.shortcuts import render
from datetime import datetime

from .models import *
from django.db.models import Q

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

        ########### Database eerst opschonen

        print("Database tabellen opschonen van " + BigIPNodes.objects.get(bigip_ip__exact=request.POST['bigip_ip']).bigip_name)

        # omdat er geen timestamp beschikbaar is van de laatste configwijziging binnen het F5 cluster
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

        # data verwijderen - profileCSSLServer tabel
        ProfileSSLServer.objects.all().filter(bigip_name_id__exact=bigip_node_id).delete()

        # data verwijderen - virtualserver tabel
        VirtualServer.objects.all().filter(bigip_name_id__exact=bigip_node_id).delete()

        # data verwijderen - database tabel
        Database.objects.all().filter(bigip_name_id__exact=bigip_node_id).delete()

        # nieuwe database entries opnemen in een dictionary voor weergave op de database.html pagina
        database_updates = {}

        ########### REST API calls

        # certificaat meldingen uitschakelen
        from requests.packages.urllib3.exceptions import InsecureRequestWarning
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        # certificaat details ophalen uit de opgegeven BigIP node
        bigip_ip = request.POST['bigip_ip']
        url = 'https://%s/mgmt/tm/sys/crypto/cert' % bigip_ip
        print("Rest API call uitvoeren " + url)
        certs = requests.get(url, headers=headers, verify=False)
        certs_list_dict = certs.json()['items']

        # client SSL profile details ophalen uit de opgegeven BigIP node
        bigip_ip = request.POST['bigip_ip']
        url = 'https://%s/mgmt/tm/ltm/profile/client-ssl' % bigip_ip
        print("Rest API call uitvoeren " + url)
        profile_cssl = requests.get(url, headers=headers, verify=False)
        profile_cssl_list_dict = profile_cssl.json()['items']

        # server SSL profile details ophalen uit de opgegeven BigIP node
        bigip_ip = request.POST['bigip_ip']
        url = 'https://%s/mgmt/tm/ltm/profile/server-ssl' % bigip_ip
        print("Rest API call uitvoeren " + url)
        profile_server_ssl = requests.get(url, headers=headers, verify=False)
        profile_server_ssl_list_dict = profile_server_ssl.json()['items']

        # virtual server details ophalen uit de opgegeven BigIP node
        # bij het wegschrijven naar de database worden ook nog API calls gedaan voor het achterhalen van de profielen
        bigip_ip = request.POST['bigip_ip']
        url = 'https://%s/mgmt/tm/ltm/virtual' % bigip_ip
        print("Rest API call uitvoeren " + url)
        virtual_servers = requests.get(url, headers=headers, verify=False)
        virtual_servers_list_dict = virtual_servers.json()['items']


        ########### Database bijwerken

        #update op basis van deze queryset
        BigIPNode = BigIPNodes.objects.get(bigip_ip=bigip_ip)

        print("Database tabellen vullen voor " + BigIPNodes.objects.get(bigip_ip__exact=request.POST['bigip_ip']).bigip_name)

        # virtual server tabel
        new_virtual_server = []

        for virtual_servers_dict in virtual_servers_list_dict:

            # bigip_name = BigIPNodes.objects.get(bigip_ip=bigip_ip)
            # full_name = virtual_servers_dict['fullPath']
            # partition = virtual_servers_dict['partition']
            # name = virtual_servers_dict['name']
            # destination = virtual_servers_dict['destination']
            # profiles = profiles_dict['name']


            # virtual server profielen toevoegen
            # profile reference dictionary aanmaken
            profile_reference = virtual_servers_dict.get('profilesReference')
            profile_link_localhost = profile_reference.get('link')
            profile_link_bigip_ip = profile_link_localhost.replace('localhost', bigip_ip)

            # API call: create list of dictionaries of profiles which are assigned to virtual servers
            profiles = requests.get(profile_link_bigip_ip, headers=headers, verify=False)
            profiles_list_dict = profiles.json()['items']

            profile_names_list = []

            for profiles_dict in profiles_list_dict:
                profile_names_list.append(profiles_dict['name'])

            #list to string
            profile_names = ','.join(profile_names_list)

            print("Virtual server tabel " + virtual_servers_dict['name'])

            BigIPNode.virtualserver_set.create(full_name=virtual_servers_dict['fullPath'],
                                               name=virtual_servers_dict['name'],
                                               partition=virtual_servers_dict['partition'],
                                               destination=virtual_servers_dict['destination'],
                                               profiles=profile_names)

            new_virtual_server.append(virtual_servers_dict['name'])


        # certificaattabel
        new_certs = []
        for cert_dict in certs_list_dict:

            #print(cert_dict)

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

            print("Certificatentabel " + cert_dict['name'])

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
            # full_name = profile_cssl_dict['fullPath']
            # partition = profile_cssl_dict['partition']
            # name = profile_cssl_dict['name']
            # cert_names = certkeychain_dict['cert']

            # loop trough certkeychain list for finding the related certificates
            certkeychain_list_dict = profile_cssl_dict.get('certKeyChain')
            cert_names_list = []

            for certkeychain_dict in certkeychain_list_dict:

                #print(certkeychain_dict['cert'])
                cert_names_list.append(certkeychain_dict['cert'])

                #list to string
                cert_names = ','.join(cert_names_list)

            print("Client SSL profile " + profile_cssl_dict['fullPath'])

            BigIPNode.profilesslclient_set.create(full_name=profile_cssl_dict['fullPath'],
                                                  partition=profile_cssl_dict['partition'],
                                                  name=profile_cssl_dict['name'],
                                                  cert_names=cert_names)

            new_profile_cssl.append(profile_cssl_dict['name'])

        # server SSL tabel
        new_profile_ssl_server = []
        for profile_server_ssl_dict in profile_server_ssl_list_dict:

            # bigip_name = BigIPNodes.objects.get(bigip_ip=bigip_ip)
            # certificate_id = Certificate.objects.filter(full_name__exact=profile_server_ssl_dict.get('Cert')).get(id))
            # full_name = profile_server_ssl_dict['fullPath']
            # partition = profile_server_ssl_dict['partition']
            # name = profile_server_ssl_dict['name']

            #print(profile_server_ssl_dict.get('cert'))
            #print(Certificates.objects.get(full_name__exact=profile_server_ssl_dict.get('cert')).id)

            print("Server SSL profile " + profile_server_ssl_dict['fullPath'])

            BigIPNode.profilesslserver_set.create(full_name=profile_server_ssl_dict['fullPath'],
                                                  certificate_id=Certificates.objects.get(full_name__exact=profile_server_ssl_dict.get('cert'),
                                                                                          bigip_name_id__exact=BigIPNodes.objects.get(bigip_ip=bigip_ip)).id if 'cert' in profile_server_ssl_dict.get('cert')!= 'none' else '',
                                                  partition=profile_server_ssl_dict['partition'],
                                                  name=profile_server_ssl_dict['name'])

            new_profile_ssl_server.append(profile_server_ssl_dict['name'])


        ########### Tabellen koppelen

        print("Database tabellen koppelen voor " + BigIPNodes.objects.get(bigip_ip__exact=request.POST['bigip_ip']).bigip_name)

        # doorloop de client SSL profielen die horen bij deze bigip en leg de many-to-many relaties met de certificatentabel
        for profilesslclient in ProfileSSLClient.objects.filter(bigip_name_id__exact=bigip_node_id):

            if profilesslclient.cert_names == '':

                # als er geen certificaten zijn gekoppeld valt er niets te doen
                continue

            else:

                # certificaten tabel query op basis van bigipname_id en partitie (partitie hoeft in dit geval niet niet,
                #  want dit is al opgenomen in de naam van de certlijst

                Certificates_query_set = Certificates.objects.filter(Q(partition__exact=profilesslclient.partition)
                                                                      | Q(partition__exact='Common'),
                                                                      bigip_name_id__exact=profilesslclient.bigip_name_id)

                # de gekoppelde certlijst doorlopen, opzoek naar een certificaat
                for cert_profilesslclient in profilesslclient.cert_names.split(','):

                    print("client ssl cert naam: " + cert_profilesslclient)

                    for cert_query_set in Certificates_query_set:

                        print("certificate name from query set: " + cert_query_set.full_name)

                        if cert_profilesslclient == cert_query_set.full_name:

                            # match gevonden --> m2m koppeltabel database_certificates_profile_ssl_client bijwerken
                            #a1.publications.add(p1)
                            print("Match gevonden en profilessl client certificates koppeltabel bijwerken")
                            cert_query_set.profilesslclient_set.add(profilesslclient)

                            break
                        else:
                            continue


        # doorloop alle virtual servers en onderliggende profielen en leg de many-to-many relaties
        for virtualserver in VirtualServer.objects.filter(bigip_name_id__exact=bigip_node_id):

            if virtualserver.profiles == '':

                # als er geen profielen zijn gekoppeld valt er niets te doen
                continue

            else:

                # profilesslclient tabel query op basis van bigipname_id en partitie

                client_ssl_profiles = ProfileSSLClient.objects.filter(Q(partition__exact=virtualserver.partition)
                                                                      | Q(partition__exact='Common'),
                                                                      bigip_name_id__exact=virtualserver.bigip_name_id)

                server_ssl_profiles = ProfileSSLServer.objects.filter(Q(partition__exact=virtualserver.partition)
                                                                      | Q(partition__exact='Common'),
                                                                      bigip_name_id__exact=virtualserver.bigip_name_id)

                # de gekoppelde profielenlijst doorlopen, opzoek naar een client- en/of server ssl profiel
                for virtual_server_profile in virtualserver.profiles.split(','):

                    # print("virtual server profile name: " + virtual_server_profile)

                    for client_ssl_profile in client_ssl_profiles:

                        # print("client ssl profile name: " + client_ssl_profile.name)

                        if virtual_server_profile == client_ssl_profile.name:

                            # match gevonden --> m2m koppeltabel virtual server en client ssl profiel bijwerken
                            client_ssl_profile.virtualserver_set.add(virtualserver)

                            break
                        else:
                            continue

                    for server_ssl_profile in server_ssl_profiles:

                        if virtual_server_profile == server_ssl_profile.name:

                            # match gevonden --> m2m koppeltabel virtual server en server ssl profiel bijwerken
                            server_ssl_profile.virtualserver_set.add(virtualserver)

                            break
                        else:
                            continue

        # toegevoegde entries meegeven om weer te geven op de database.html pagina
        database_updates['certificates'] = new_certs
        database_updates['profile_cssl'] = new_profile_cssl
        database_updates['profile_ssl_server'] = new_profile_ssl_server
        database_updates['virtual_servers'] = new_virtual_server

        # database tabel bijwerken zodat het duidelijk is van welke datum de huidige configuratie is
        #bigip_name_id = BigIPNodes.objects.get(full_name__exact=).id
        BigIPNode.database_set.create()

        context = {'database_updates' : database_updates}

    return render(request, 'database/database.html', context)