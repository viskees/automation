from django.core.management.base import BaseCommand
from datetime import datetime
import requests
from database.models import *
from certificates.models import *
from django.db.models import Q

class Command(BaseCommand):
    help = 'update the database of all cluster'

    def handle(self, *args, **kwargs):
        # self.stdout.write(virtual_server.name)

        # headers voor de API calls
        headers = {'Authorization': 'Basic YWRtaW46YWRtaW4=', 'Content-Type': 'application/json'}

        for node in BigIPNodes.objects.all():

            #print('updating: ' + node.bigip_ip)

            ########### Database eerst opschonen

            # omdat er geen timestamp beschikbaar is van de laatste configwijziging binnen het F5 cluster
            # kan er niet worden bepaald of bepaalde tabellen moeten worden bijgewerkt.
            # Daarom worden alle configuratietabellen die horen bij het betreffende F5 cluster opnieuw opgebouwd.

            # verwijderen huidige tabel data voor de betreffende BigIP node
            # queryset maken van alle data wat hoort bij de betreffende BigIP node
            # achterhalen van het pkid van de BigIP node waarvoor een update wordt gevraagd

            bigip_ip = node.bigip_ip

            bigip_node_id = BigIPNodes.objects.get(bigip_ip__exact=bigip_ip).id

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

            # data verwijderen - CertClientSSLVirtualServer tabel
            CertClientSSLVirtualServer.objects.all().delete()

            # data verwijderen - CertServerSSLVirtualServer tabel
            CertServerSSLVirtualServer.objects.all().delete()

            ########### REST API calls

            # certificaat details ophalen uit de opgegeven BigIP node
            url = 'https://%s/mgmt/tm/sys/crypto/cert' % bigip_ip
            certs = requests.get(url, headers=headers, verify=False)
            certs_list_dict = certs.json()['items']

            # client SSL profile details ophalen uit de opgegeven BigIP node
            url = 'https://%s/mgmt/tm/ltm/profile/client-ssl' % bigip_ip
            profile_cssl = requests.get(url, headers=headers, verify=False)
            profile_cssl_list_dict = profile_cssl.json()['items']

            # server SSL profile details ophalen uit de opgegeven BigIP node
            url = 'https://%s/mgmt/tm/ltm/profile/server-ssl' % bigip_ip
            profile_server_ssl = requests.get(url, headers=headers, verify=False)
            profile_server_ssl_list_dict = profile_server_ssl.json()['items']

            # virtual server details ophalen uit de opgegeven BigIP node
            # bij het wegschrijven naar de database worden ook nog API calls gedaan voor het achterhalen van de profielen
            url = 'https://%s/mgmt/tm/ltm/virtual' % bigip_ip
            virtual_servers = requests.get(url, headers=headers, verify=False)
            virtual_servers_list_dict = virtual_servers.json()['items']

            ########### Database bijwerken

            # update op basis van deze queryset
            BigIPNode = BigIPNodes.objects.get(bigip_ip=bigip_ip)

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

                # list to string
                profile_names = ','.join(profile_names_list)

                BigIPNode.virtualserver_set.create(full_name=virtual_servers_dict['fullPath'],
                                                   name=virtual_servers_dict['name'],
                                                   partition=virtual_servers_dict['partition'],
                                                   destination=virtual_servers_dict['destination'],
                                                   profiles=profile_names)

                new_virtual_server.append(virtual_servers_dict['name'])

            # certificaattabel
            new_certs = []
            for cert_dict in certs_list_dict:
                # print(cert_dict)

                # bigip_name = BigIPNodes.objects.get(bigip_ip=bigip_ip)
                # name = cert_name form cert_dict['name'].split("/")
                # full_name = cert_dict['name']
                # partition = cert_partition cert_dict['name'].split("/")
                # expiration = cert_dict['apiRawValues']['expiration']
                # commonName = cert_dict['commonName']
                # certificateKeySize = cert_dict['apiRawValues']['certificateKeySize']
                # publicKeyType = cert_dict['apiRawValues']['publicKeyType']
                # organization = cert_dict['commonName']
                # ou = cert_dict['ou']
                # city = cert_dict['city']
                # country = cert_dict['country']
                # state = cert_dict['state']
                # subjectAlternativeName = cert_dict['subjectAlternativeName']

                slash, cert_partition, cert_name = cert_dict['name'].split("/")

                BigIPNode.certificates_set.create(bigip_name=BigIPNodes.objects.get(bigip_ip=bigip_ip),
                                                  name=cert_name,
                                                  full_name=cert_dict['name'],
                                                  partition=cert_partition,
                                                  expiration=datetime.strptime(cert_dict['apiRawValues']['expiration'],
                                                                               '%b %d %H:%M:%S %Y %Z'),
                                                  commonName=cert_dict['commonName'],
                                                  certificateKeySize=cert_dict['apiRawValues']['certificateKeySize'],
                                                  publicKeyType=cert_dict['apiRawValues']['publicKeyType'],
                                                  organization=cert_dict[
                                                      'commonName'] if 'organization' in cert_dict.keys() else '',
                                                  ou=cert_dict['ou'] if 'ou' in cert_dict.keys() else '',
                                                  city=cert_dict['city'] if 'city' in cert_dict.keys() else '',
                                                  country=cert_dict['country'] if 'country' in cert_dict.keys() else '',
                                                  state=cert_dict['state'] if 'state' in cert_dict.keys() else '',
                                                  subjectAlternativeName=cert_dict[
                                                      'subjectAlternativeName'] if 'subjectAlternativeName' in cert_dict.keys() else ''
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
                    # print(certkeychain_dict['cert'])
                    cert_names_list.append(certkeychain_dict['cert'])

                    # list to string
                    cert_names = ','.join(cert_names_list)

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

                # print(profile_server_ssl_dict.get('cert'))
                # print(Certificates.objects.get(full_name__exact=profile_server_ssl_dict.get('cert')).id)

                BigIPNode.profilesslserver_set.create(full_name=profile_server_ssl_dict['fullPath'],
                                                      certificate_id=Certificates.objects.get(
                                                          full_name__exact=profile_server_ssl_dict.get('cert'),
                                                          bigip_name_id__exact=BigIPNodes.objects.get(
                                                              bigip_ip=bigip_ip)).id if 'cert' in profile_server_ssl_dict.get(
                                                          'cert') != 'none' else '',
                                                      partition=profile_server_ssl_dict['partition'],
                                                      name=profile_server_ssl_dict['name'])

                new_profile_ssl_server.append(profile_server_ssl_dict['name'])

            ########### Tabellen koppelen

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

                        # print("client ssl cert naam: " + cert_profilesslclient)

                        for cert_query_set in Certificates_query_set:

                            # print("certificate name from query set: " + cert_query_set.full_name)

                            if cert_profilesslclient == cert_query_set.full_name:

                                # match gevonden --> m2m koppeltabel database_certificates_profile_ssl_client bijwerken
                                # a1.publications.add(p1)
                                cert_query_set.profile_ssl_client.add(profilesslclient)

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
                                client_ssl_profile.virtual_server.add(virtualserver)

                                break
                            else:
                                continue

                        for server_ssl_profile in server_ssl_profiles:

                            if virtual_server_profile == server_ssl_profile.name:

                                # match gevonden --> m2m koppeltabel virtual server en server ssl profiel bijwerken
                                server_ssl_profile.virtual_server.add(virtualserver)

                                break
                            else:
                                continue

            # verzameltabel CertClientSSLVirtualServer opbouwen waarmee de certificaten op verloopdatum kunnen worden gesorteerd.
            #
            # zowel de vitual server als de client ssl profielen kunnen vaker zijn toegepast per certificaat.
            #
            # cert_name = cert_from_db_app.full_name
            # cert_partition = cert_from_db_app.partition
            # cert_expiration = cert_from_db_app.expiration
            # cert_cluster = BigIPNodes.objects.get(pk=cert_from_db_app.bigip_name_id)
            # cssl_name = cssl_from_db_app.full_name
            # cssl_partition = cssl_from_db_app.partition
            # vs_name = vs_from_db_app.full_name
            # vs_partition = vs_from_db_app.partition
            # vs_ip =  vs_from_db_app.destination
            #

            for cert_from_db_app in Certificates.objects.all():

                # print('cert name: ' + cert_from_db_app.full_name)

                # maak per client ssl profiel een certvs entry in de CertClientSSLVirtualServer tabel
                for cssl_from_db_app in ProfileSSLClient.objects.filter(
                        certificates__full_name__exact=cert_from_db_app.full_name,
                        bigip_name_id__exact=cert_from_db_app.bigip_name_id):

                    # print('cssl name: ' + cssl_from_db_app.full_name)

                    # en breidt dit uit met virtual server configuratie informatie
                    for vs_from_db_app in VirtualServer.objects.filter(
                            profilesslclient__full_name=cssl_from_db_app.full_name,
                            bigip_name_id__exact=cssl_from_db_app.bigip_name_id):
                        # print('virtual server name: ' + vs_from_db_app.full_name)
                        # voeg een nieuwe certificaatregel toe per virtual server in de CertClientSSLVirtualServer tabel
                        cert_clientssl_virtualserver = CertClientSSLVirtualServer(
                            cert_name=cert_from_db_app.full_name,
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
                    # print(ProfileSSLServer.objects.filter(certificate_id__exact=cert_from_db_app.id).values())

                    for server_ssl_from_db_app in ProfileSSLServer.objects.filter(
                            certificate_id__exact=cert_from_db_app.id,
                            bigip_name_id__exact=cert_from_db_app.bigip_name_id):

                        # print('server ssl name: ' + server_ssl_from_db_app.full_name)

                        # en breidt dit uit met virtual server configuratie informatie
                        for vs_from_db_app in VirtualServer.objects.filter(
                                profilesslserver__full_name=server_ssl_from_db_app.full_name,
                                bigip_name_id__exact=server_ssl_from_db_app.bigip_name_id):
                            # print('virtual server name: ' + vs_from_db_app.full_name)

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

            # database tabel bijwerken zodat het duidelijk is van welke datum de huidige configuratie is

            BigIPNode.database_set.create()