from django.core.management.base import BaseCommand
from datetime import datetime
import requests
from database.models import *
from certificates.models import *
from virtualservers.models import *
from django.db.models import Q

class Command(BaseCommand):
    help = 'update the database of all cluster'

    def handle(self, *args, **kwargs):
        # self.stdout.write(virtual_server.name)

        # headers voor de API calls
        headers = {'Authorization': 'Basic YWRtaW46YWRtaW4=', 'Content-Type': 'application/json'}

        for node in BigIPNodes.objects.all():

            # print('updating: ' + node.bigip_ip)

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

            # data verwijderen - irule tabel
            Irule.objects.all().filter(bigip_name_id__exact=bigip_node_id).delete()

            # data verwijderen - datagroup tabel
            Datagroup.objects.all().filter(bigip_name_id__exact=bigip_node_id).delete()

            # data verwijderen - database tabel
            Database.objects.all().filter(bigip_name_id__exact=bigip_node_id).delete()

            ########### Database van de certificaten app eerst opschonen

            # data verwijderen - CertClientSSLVirtualServer tabel
            CertClientSSLVirtualServer.objects.all().delete()

            # data verwijderen - CertServerSSLVirtualServer tabel
            CertServerSSLVirtualServer.objects.all().delete()

            # data verwijderen - CertServerSSLVirtualServerViaIruleAndDatagroup tabel
            CertServerSSLVirtualServerViaIruleAndDatagroup.objects.all().delete()

            ########### Database van de virtualservs app eerst opschonen

            # data verwijderen - VirtualServer tabel
            VirtualServerCluster.objects.all().delete()

            # nieuwe database entries opnemen in een dictionary voor weergave op de database.html pagina
            database_updates = {}

            ########### REST API calls

            # certificaatmeldingen uitschakelen
            from requests.packages.urllib3.exceptions import InsecureRequestWarning
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

            # datagroup details ophalen uit de opgegeven BigIP node
            url = 'https://%s/mgmt/tm/ltm/data-group/internal' % bigip_ip
            print("Rest API call uitvoeren " + url)
            datagroups = requests.get(url, headers=headers, verify=False)
            datagroups_list_dict = datagroups.json()['items']

            # ilrule details ophalen uit de opgegeven BigIP node
            url = 'https://%s/mgmt/tm/ltm/rule' % bigip_ip
            print("Rest API call uitvoeren " + url)
            irules = requests.get(url, headers=headers, verify=False)
            irules_list_dict = irules.json()['items']

            # certificaat details ophalen uit de opgegeven BigIP node
            url = 'https://%s/mgmt/tm/sys/crypto/cert' % bigip_ip
            print("Rest API call uitvoeren " + url)
            certs = requests.get(url, headers=headers, verify=False)
            certs_list_dict = certs.json()['items']

            # client SSL profile details ophalen uit de opgegeven BigIP node
            url = 'https://%s/mgmt/tm/ltm/profile/client-ssl' % bigip_ip
            print("Rest API call uitvoeren " + url)
            profile_cssl = requests.get(url, headers=headers, verify=False)
            profile_cssl_list_dict = profile_cssl.json()['items']

            # server SSL profile details ophalen uit de opgegeven BigIP node
            url = 'https://%s/mgmt/tm/ltm/profile/server-ssl' % bigip_ip
            print("Rest API call uitvoeren " + url)
            profile_server_ssl = requests.get(url, headers=headers, verify=False)
            profile_server_ssl_list_dict = profile_server_ssl.json()['items']

            # virtual server details ophalen uit de opgegeven BigIP node
            # bij het wegschrijven naar de database worden ook nog API calls gedaan voor het achterhalen van de profielen
            url = 'https://%s/mgmt/tm/ltm/virtual' % bigip_ip
            print("Rest API call uitvoeren " + url)
            virtual_servers = requests.get(url, headers=headers, verify=False)
            virtual_servers_list_dict = virtual_servers.json()['items']

            ########### Database bijwerken

            # update op basis van deze queryset
            BigIPNode = BigIPNodes.objects.get(bigip_ip=bigip_ip)

            ##template
            #
            '''
            new_datagroups = []
            for datagroup_dict in datagroups_list_dict:
                # print(datagroup_dict)
                slash, cert_partition, cert_name = cert_dict['name'].split("/")
                print("Datagrouptabel " + cert_dict['name'])
                print(datagroup_dict['name'])
                BigIPNode.datagroup_set.create(bigip_name=BigIPNodes.objects.get(bigip_ip=bigip_ip),
                                                  )
                new_datagroups.append(datagroup_dict['name'])
            '''

            # datagrouptabel
            new_datagroups = []

            # de volgende datagroups verwijzen naar een server SSL profile;
            datagroup_to_be_queried = ['clientAuthorisationDataGroup',
                                       'webservices-outgoingClientAuthorisationDataGroup',
                                       'ProdClientAuthorisationDataGroup',
                                       'dg_ilt-integratie-outbound-clientAuthorisation']

            for datagroup_dict in datagroups_list_dict:

                datagroup_profile_server_ssl_list = []

                if datagroup_dict['name'] in datagroup_to_be_queried:

                    # doorzoek de huidige datagroup op server ssl profiles
                    for datagroup_record in datagroup_dict['records']:
                        datagroup_profile_server_ssl_list.append(datagroup_record['data'])

                # datagroup_profile_server_ssl_list to string
                datagroup_profile_server_ssl = ",".join(datagroup_profile_server_ssl_list)

                # schrijf datagroup gerecord naar database met de volgende velden
                # bigip_name = BigIPNodes.objects.get(bigip_ip=bigip_ip)
                # full_name = datagroup_dict['fullPath']
                # name = datagroup_dict['name']
                # partition = datagroup_dict['partition']
                # datagroup_profile_server_ssl

                # slash, datagroup_partition, datagroup_name = datagroup_dict['fullPath'].split("/")

                print("Datagrouptabel " + datagroup_dict['name'])

                BigIPNode.datagroup_set.create(bigip_name=BigIPNodes.objects.get(bigip_ip=bigip_ip),
                                               full_name=datagroup_dict['fullPath'],
                                               name=datagroup_dict['name'],
                                               partition=datagroup_dict['partition'],
                                               datagroup_profile_server_ssl=datagroup_profile_server_ssl
                                               )

                new_datagroups.append(datagroup_dict['name'])

            # iruletabel
            new_irules = []
            for irule_dict in irules_list_dict:

                # print(irule_dict)

                # bigip_name = BigIPNodes.objects.get(bigip_ip=bigip_ip)
                # datagroup = m2m koppeling
                # full_name = irule_dict['fullPath']
                # partition = irule_dict['partition']
                # irule_content = irule_dict['apiAnonymous']
                # datagroups = --> irule_content parsen op datagroups

                # check irule for datagroups content obv de datagroup tabel
                irule_datagroups_names_list = []

                for datagroup in Datagroup.objects.filter(
                        Q(partition__exact=irule_dict['partition']) | Q(partition__exact='Common'),
                        bigip_name_id__exact=BigIPNodes.objects.get(bigip_ip=bigip_ip).id):

                    print(irule_dict['fullPath'] + " wordt nu doorzocht op aanwezigheid van datagroup " + datagroup.name)

                    # test of de irule data bevat of leeg is
                    if 'apiAnonymous' in irule_dict:

                        if datagroup.name in irule_dict['apiAnonymous']:
                            print('Datagroup ' + datagroup.name + ' gevonden in irule: ' + irule_dict['fullPath'])

                            irule_datagroups_names_list.append(datagroup.full_name)

                print("Iruletabel " + irule_dict['name'])

                # datagroup list to string

                irule_datagroups_names = ','.join(irule_datagroups_names_list)

                BigIPNode.irule_set.create(bigip_name=BigIPNodes.objects.get(bigip_ip=bigip_ip),
                                           full_name=irule_dict['fullPath'],
                                           partition=irule_dict['partition'],
                                           irule_content = irule_dict['apiAnonymous'] if 'apiAnonymous' in irule_dict.keys() else '',
                                           datagroups=irule_datagroups_names
                                           )

                new_irules.append(irule_dict['name'])

            # virtual server tabel
            new_virtual_server = []

            for virtual_servers_dict in virtual_servers_list_dict:

                # bigip_name = BigIPNodes.objects.get(bigip_ip=bigip_ip)
                # full_name = virtual_servers_dict['fullPath']
                # partition = virtual_servers_dict['partition']
                # name = virtual_servers_dict['name']
                # destination = virtual_servers_dict['destination']
                # profiles = profiles_dict['name']
                # irules = virtual_servers_dict['rules']

                # virtual server profielen toevoegen
                # profile reference dictionary aanmaken
                profile_reference = virtual_servers_dict.get('profilesReference')
                profile_link_localhost = profile_reference.get('link')
                profile_link_bigip_ip = profile_link_localhost.replace('localhost', bigip_ip)

                # API call: create list of dictionaries of profiles which are assigned to virtual servers
                profiles = requests.get(profile_link_bigip_ip, headers=headers, verify=False)
                profiles_list_dict = profiles.json()['items']

                # profiles list to string
                profile_names_list = []

                for profiles_dict in profiles_list_dict:
                    profile_names_list.append(profiles_dict['name'])

                profile_names = ','.join(profile_names_list)

                # irule list
                irule_names_list = []
                # eerst testen of er wel irules zijn gekoppeld

                if 'rules' in virtual_servers_dict:

                    for irule in virtual_servers_dict['rules']:
                        irule_names_list.append(irule)

                # irule list to string
                irule_names = ','.join(irule_names_list)

                print("Virtual server tabel " + virtual_servers_dict['name'])

                BigIPNode.virtualserver_set.create(full_name=virtual_servers_dict['fullPath'],
                                                   name=virtual_servers_dict['name'],
                                                   partition=virtual_servers_dict['partition'],
                                                   destination=virtual_servers_dict['destination'],
                                                   profiles=profile_names,
                                                   irules=irule_names
                                                   )

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

                print("Certificatentabel " + cert_dict['name'])

                # print(cert_dict['name'])

                BigIPNode.certificates_set.create(bigip_name=BigIPNodes.objects.get(bigip_ip=bigip_ip),
                                                  name=cert_name,
                                                  full_name=cert_dict['name'],
                                                  partition=cert_partition,
                                                  expiration=datetime.strptime(cert_dict['apiRawValues']['expiration'],
                                                                               '%b %d %H:%M:%S %Y %Z'),
                                                  commonName=cert_dict[
                                                      'commonName'] if 'commonName' in cert_dict.keys() else '',
                                                  certificateKeySize=cert_dict['apiRawValues']['certificateKeySize'],
                                                  publicKeyType=cert_dict['apiRawValues']['publicKeyType'],
                                                  organization=cert_dict[
                                                      'organization'] if 'organization' in cert_dict.keys() else '',
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

                # print('SSL server profile name: ' + profile_server_ssl_dict.get('fullPath'))
                # print('SSL server profile cert name: ' + profile_server_ssl_dict.get('cert'))
                # print('BigIP id: ' + str(BigIPNodes.objects.get(bigip_ip=bigip_ip).id))

                if profile_server_ssl_dict.get('cert') != 'none':
                    cert_ssl_server_profile = Certificates.objects.all().filter(
                        full_name__exact=profile_server_ssl_dict.get('cert'),
                        bigip_name_id__exact=BigIPNodes.objects.get(bigip_ip=bigip_ip).id)

                    certificate_id = cert_ssl_server_profile[0].id
                    # print('bijbehorende certificate ID op basis van filter query: ' + str(cert_ssl_server_profile[0].id))

                else:
                    certificate_id = ''

                # print('bijbehorende certificate ID op basis GET query' + str(Certificates.objects.get(full_name__exact=profile_server_ssl_dict.get('cert'),
                #                                                                              bigip_name_id__exact=BigIPNodes.objects.get(bigip_ip=bigip_ip).id).id if 'cert' in profile_server_ssl_dict.get('cert')!= 'none' else '',))

                print("Server SSL profile " + profile_server_ssl_dict['fullPath'])

                BigIPNode.profilesslserver_set.create(full_name=profile_server_ssl_dict['fullPath'],
                                                      certificate_id=certificate_id,
                                                      # certificate_id=Certificates.objects.get(full_name__exact=profile_server_ssl_dict.get('cert'),
                                                      #                                        bigip_name_id__exact=BigIPNodes.objects.get(bigip_ip=bigip_ip).id).id if 'cert' in profile_server_ssl_dict.get('cert')!= 'none' else '',
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

                        print("client ssl cert naam: " + cert_profilesslclient)

                        for cert_query_set in Certificates_query_set:

                            print("certificate name from query set: " + cert_query_set.full_name)

                            if cert_profilesslclient == cert_query_set.full_name:

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

                                print('match gevonden --> m2m koppeltabel voor client ssl profiel ' + client_ssl_profile.name )
                                client_ssl_profile.virtualserver_set.add(virtualserver)

                                break
                            else:
                                continue

                        for server_ssl_profile in server_ssl_profiles:

                            if virtual_server_profile == server_ssl_profile.name:

                                print('match gevonden --> m2m koppeltabel voor server ssl profiel ' + server_ssl_profile.name )
                                server_ssl_profile.virtualserver_set.add(virtualserver)

                                break
                            else:
                                continue

                if virtualserver.irules == '':

                    # als er geen irules zijn gekoppeld valt er niets te doen
                    continue

                else:

                    # irule tabel query op basis van bigipname_id en partitie
                    irules_db_query = Irule.objects.filter(Q(partition__exact=virtualserver.partition)
                                                           | Q(partition__exact='Common'),
                                                           bigip_name_id__exact=virtualserver.bigip_name_id)

                    # de gekoppelde profielenlijst doorlopen, opzoek naar een client- en/of server ssl profiel
                    for virtual_server_irule in virtualserver.irules.split(','):

                        for irule in irules_db_query:

                            if virtual_server_irule == irule.full_name:

                                print('match gevonden --> m2m koppeltabel voor irule ' + irule.full_name )
                                irule.virtualserver_set.add(virtualserver)

                                # uitzondering voor de volgende irules omdat hier nog datagroups aan gekoppeld moeten worden
                                # waarbij de partitie van de datagroup gelijk is aan dit van de virtual server

                                irule_exception_list = ['/Common/irule_webservices.dictu.nl_tls-proxy_outbound']
                                irule_exception_datagroups_names_list = []

                                if irule.full_name in irule_exception_list:

                                    # doorzoek deze irule op de volgende datagroupen

                                    for datagroup in Datagroup.objects.filter(Q(partition__exact=virtualserver.partition)
                                            | Q(partition__exact='Common'),
                                            bigip_name_id__exact=BigIPNodes.objects.get(bigip_ip=bigip_ip).id):

                                        print("UITZONDERING!: " + irule.full_name
                                              + " wordt nu doorzocht op aanwezigheid van datagroup " + datagroup.name)

                                        if datagroup.name in irule.irule_content:
                                            print('Datagroup ' + datagroup.name + ' gevonden in irule: ' + irule.full_name)

                                            irule_exception_datagroups_names_list.append(datagroup.full_name)

                                    # datagroup list to string

                                    irule_exception_datagroups_names = ','.join(irule_exception_datagroups_names_list)

                                    # irule entry aanpassen (datagroups toevoegen)
                                    irule.datagroups += irule_exception_datagroups_names
                                    irule.save()

                                break
                            else:
                                continue

            # doorloop alle irules en onderliggende datagroup profielen en leg de many-to-many relaties
            print('irule tabel doorlopen voor het leggen van de m2m relaties met de datagroupstabel')

            for irule in Irule.objects.filter(bigip_name_id__exact=bigip_node_id):

                if irule.datagroups == '':

                    # als er geen datagroups zijn gekoppeld valt er niets te doen
                    continue

                else:

                    # datagroup tabel query op basis van bigipname_id en partitie

                    #datagroup_db_query = Datagroup.objects.filter(Q(partition__exact=irule.partition)
                    #                                              | Q(partition__exact='Common'),
                    #                                              bigip_name_id__exact=irule.bigip_name_id)

                    # omdat er ook irules in de common partitie zijn opgenomen met datagroups uit andere partities
                    # moeten we alle datagroups doorlopen
                    datagroup_db_query = Datagroup.objects.all()

                    # de gekoppelde profielenlijst doorlopen, opzoek naar een client- en/of server ssl profiel
                    for irule_datagroup_name in irule.datagroups.split(','):

                        print("irule datagroup name: " + irule_datagroup_name)

                        for datagroup in datagroup_db_query:

                            print("db datagroup name from query : " + datagroup.full_name)

                            if irule_datagroup_name == datagroup.full_name:

                                print('match gevonden --> m2m koppeltabel irule en datagroup bijwerken')
                                irule.datagroup.add(datagroup)
                                break
                            else:
                                continue

            # doorloop alle datagroups en onderliggende server ssl profielen en leg de many-to-many relaties
            print('datagroup tabel doorlopen voor het leggen van de m2m relaties met de server ssl tabel')

            for datagroup in Datagroup.objects.filter(bigip_name_id__exact=bigip_node_id):

                if datagroup.datagroup_profile_server_ssl == '':

                    # als er geen server ssl profielen zijn gekoppeld valt er niets te doen
                    continue

                else:

                    # profile server ssl tabel query op basis van bigipname_id en partitie

                    profile_ssl_server_query = ProfileSSLServer.objects.filter(Q(partition__exact=datagroup.partition)
                                                                               | Q(partition__exact='Common'),
                                                                               bigip_name_id__exact=datagroup.bigip_name_id)

                    # de gekoppelde profielenlijst doorlopen, opzoek naar een client- en/of server ssl profiel
                    for datagroup_profile_server_ssl_name in datagroup.datagroup_profile_server_ssl.split(','):

                        print("datagroup server ssl profile name: " + datagroup_profile_server_ssl_name)

                        for profile_ssl_server in profile_ssl_server_query:

                            print("db profile_ssl_server name from query : " + profile_ssl_server.full_name)

                            if datagroup_profile_server_ssl_name == profile_ssl_server.full_name:

                                print('match gevonden --> m2m koppeltabel datagroup en server SSL profile bijwerken')
                                datagroup.profile_server_ssl.add(profile_ssl_server)
                                break
                            else:
                                continue

            # verzameltabellen van de verschillende app's vullen
            # certificates app

            for cert_from_db_app in Certificates.objects.all():

                # print('cert name: ' + cert_from_db_app.full_name)

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
                for cssl_from_db_app in ProfileSSLClient.objects.filter(
                        certificates__full_name__exact=cert_from_db_app.full_name,
                        bigip_name_id__exact=cert_from_db_app.bigip_name_id):

                    # print('cssl name: ' + cssl_from_db_app.full_name)

                    # en breidt dit uit met virtual server configuratie informatie
                    for vs_from_db_app in VirtualServer.objects.filter(
                            profile_client_ssl__full_name=cssl_from_db_app.full_name,
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
                                profile_server_ssl__full_name=server_ssl_from_db_app.full_name,
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

                        # certificaten die gekoppeld zijn aan een virtual server via irules/data groups worden toegevoegd
                        # aan tabel CertServerSSLVirtualServerViaIruleAndDatagroup

                        for datagroup_from_db_app in Datagroup.objects.filter(
                                profile_server_ssl__full_name=server_ssl_from_db_app.full_name,
                                bigip_name_id__exact=server_ssl_from_db_app.bigip_name_id):

                            print(
                                server_ssl_from_db_app.full_name + ' gevonden voor datagroup ' + datagroup_from_db_app.full_name)

                            # op zoek naar irules waar deze datagroup aan naar verwijst

                            for irule_from_db_app in Irule.objects.filter(
                                    datagroup__full_name=datagroup_from_db_app.full_name,
                                    bigip_name_id__exact=datagroup_from_db_app.bigip_name_id):

                                print(
                                    datagroup_from_db_app.full_name + ' gevonden voor ' + irule_from_db_app.full_name)

                                # op zoek naar virtual servers waar deze irule naar verwijst

                                for vs_from_db_app in VirtualServer.objects.filter(
                                        irule__full_name=irule_from_db_app.full_name,
                                        bigip_name_id__exact=irule_from_db_app.bigip_name_id):
                                    print(
                                        irule_from_db_app.full_name + ' gevonden voor virtual server ' + vs_from_db_app.full_name)

                                    # voeg een nieuwe certificaatregel toe per virtual server
                                    # in de CertServerSSLVirtualServerViaIruleAndDatagroup tabel
                                    # cert_name = cert_from_db_app.full_name,
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
                                        cert_partition=cert_from_db_app.partition,
                                        cert_expiration=cert_from_db_app.expiration,
                                        cert_cluster=BigIPNodes.objects.get(pk=cert_from_db_app.bigip_name_id),
                                        server_ssl_name=server_ssl_from_db_app.full_name,
                                        server_ssl_partition=server_ssl_from_db_app.partition,
                                        irule_name=irule_from_db_app.full_name,
                                        datagroup_name=datagroup_from_db_app.full_name,
                                        vs_name=vs_from_db_app.full_name,
                                        vs_partition=vs_from_db_app.partition,
                                        vs_ip=vs_from_db_app.destination)

                                    cert_irule_virtualserver.save()


                else:
                    continue

            # verzameltabellen van de verschillende app's vullen
            # virtualservers app

            # virtualserver tabel doorlopen uit de DB app en de virtualserverclustertabel vullen
            for vs_from_db_app in VirtualServer.objects.all():

                # verzameltabel virtualserverclustertabel opbouwen.
                #
                # vs_name = vs_from_db_app.full_name
                # vs_ip = vs_from_db_app.destination
                # vs_cluster = BigIPNodes.objects.get(pk=vs_from_db_app.bigip_name_id)

                virtualserver_cluster = VirtualServerCluster(vs_name = vs_from_db_app.full_name,
                                                             vs_ip = vs_from_db_app.destination,
                                                             vs_cluster = BigIPNodes.objects.get(pk=vs_from_db_app.bigip_name_id))

                virtualserver_cluster.save()


            # database tabel bijwerken zodat het duidelijk is van welke datum de huidige configuratie is

            BigIPNode.database_set.create()
