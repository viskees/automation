from django.core.management.base import BaseCommand
from datetime import datetime
import requests
from database.models import BigIPNodes, Certificates, ProfileSSLClient, Database, VirtualServer
from django.db.models import Q

class Command(BaseCommand):
    help = 'update the database of all cluster'

    def handle(self, *args, **kwargs):
        # self.stdout.write(virtual_server.name)

        # headers voor de API calls
        headers = {'Authorization': 'Basic 123456', 'Content-Type': 'application/json'}

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

            # data verwijderen - virtualserver tabel
            VirtualServer.objects.all().filter(bigip_name_id__exact=bigip_node_id).delete()

            # data verwijderen - database tabel
            Database.objects.all().filter(bigip_name_id__exact=bigip_node_id).delete()



            ########### REST API calls

            # certificaat details ophalen uit de opgegeven BigIP node
            url = 'https://%s/mgmt/tm/sys/crypto/cert' % bigip_ip
            certs = requests.get(url, headers=headers, verify=False)
            certs_list_dict = certs.json()['items']

            # client SSL profile details ophalen uit de opgegeven BigIP node
            url = 'https://%s/mgmt/tm/ltm/profile/client-ssl' % bigip_ip
            profile_cssl = requests.get(url, headers=headers, verify=False)
            profile_cssl_list_dict = profile_cssl.json()['items']

            # virtual server details ophalen uit de opgegeven BigIP node
            # bij het wegschrijven naar de database worden ook nog API calls gedaan voor het achterhalen van de profielen
            url = 'https://%s/mgmt/tm/ltm/virtual' % bigip_ip
            virtual_servers = requests.get(url, headers=headers, verify=False)
            virtual_servers_list_dict = virtual_servers.json()['items']


            ########### Database bijwerken

            #update op basis van deze queryset
            BigIPNode = BigIPNodes.objects.get(bigip_ip=bigip_ip)

            # certificaattabel

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

                BigIPNode.certificates_set.create(bigip_name = BigIPNodes.objects.get(bigip_ip=bigip_ip),
                                                  name=cert_name,
                                                  full_name=cert_dict['name'],
                                                  partition=cert_partition,
                                                  expiration=datetime.strptime(cert_dict['apiRawValues']['expiration'],
                                                                               '%b %d %H:%M:%S %Y %Z'),
                                                  commonName = cert_dict['commonName'] if 'commonName' in cert_dict.keys() else '',
                                                  certificateKeySize = cert_dict['apiRawValues']['certificateKeySize'],
                                                  publicKeyType = cert_dict['apiRawValues']['publicKeyType'],
                                                  organization = cert_dict['organization'] if 'organization' in cert_dict.keys() else '',
                                                  ou = cert_dict['ou'] if 'ou' in cert_dict.keys() else '',
                                                  city = cert_dict['city'] if 'city' in cert_dict.keys() else '',
                                                  country = cert_dict['country'] if 'country' in cert_dict.keys() else '',
                                                  state = cert_dict['state'] if 'state' in cert_dict.keys() else '',
                                                  subjectAlternativeName=cert_dict['subjectAlternativeName'] if 'subjectAlternativeName' in cert_dict.keys() else ''
                                                      )

            # client SSL tabel

            for profile_cssl_dict in profile_cssl_list_dict:

                # bigip_name = BigIPNodes.objects.get(bigip_ip=bigip_ip)
                # certificate_id = Certificates.objects.get(full_name__exact=profile_cssl_dict['fullPath']).id
                # full_name = profile_cssl_dict['fullPath']
                # partition = profile_cssl_dict['partition']
                # name = profile_cssl_dict['name']

                certificate_id = Certificates.objects.get(full_name__exact=profile_cssl_dict['cert'],
                                                          bigip_name_id__exact=bigip_node_id).id
                BigIPNode.profilesslclient_set.create(certificate_id=certificate_id,
                                                      full_name=profile_cssl_dict['fullPath'],
                                                      partition=profile_cssl_dict['partition'],
                                                      name=profile_cssl_dict['name'])


            # virtual server tabel

            for virtual_servers_dict in virtual_servers_list_dict:

                # bigip_name = BigIPNodes.objects.get(bigip_ip=bigip_ip)
                # profilesslclient_id = profilesslclient.objects.get(name__exact=profiles_dict['name']).id
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

                BigIPNode.virtualserver_set.create(full_name=virtual_servers_dict['fullPath'],
                                                   name=virtual_servers_dict['name'],
                                                   partition=virtual_servers_dict['partition'],
                                                   destination=virtual_servers_dict['destination'],
                                                   profiles=profile_names)


            ########### Tabellen koppelen

            # virtual server profilesslclient_id
            # doorloop alle virtual servers
            for virtualserver in VirtualServer.objects.filter(bigip_name_id__exact=bigip_node_id):

                if virtualserver.profiles == '':

                    # als er geen profielen zijn gekoppeld valt er niets te doen
                    continue

                else:

                    # profilesslclient tabel query op basis van bigipname_id en partitie
                    client_ssl_profiles = ProfileSSLClient.objects.filter(Q(partition__exact=virtualserver.partition)
                                                                          | Q(partition__exact='Common'),
                                                                          bigip_name_id__exact=virtualserver.bigip_name_id)

                    # de gekoppelde profielenlijst doorlopen, opzoek naar een client ssl profiel
                    for virtual_server_profile in virtualserver.profiles.split(','):

                        #print("virtual server profile name: " + virtual_server_profile)

                        for client_ssl_profile in client_ssl_profiles:

                           #print("client ssl profile name: " + client_ssl_profile.name)

                            if virtual_server_profile==client_ssl_profile.name:
                                #match gevonden --> update virtual server tabel
                                VirtualServer.objects.filter(name__exact=virtualserver.name,
                                                                   bigip_name_id__exact=virtualserver.bigip_name_id,
                                                                   partition__exact=virtualserver.partition).\
                                    update(profilesslclient_id=client_ssl_profile.id)
                                break
                            else:
                                continue




            # database tabel bijwerken zodat het duidelijk is van welke datum de huidige configuratie is

            BigIPNode.database_set.create()
