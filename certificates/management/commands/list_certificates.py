from django.core.management.base import BaseCommand
from database.models import *
from certificates.models import *
from django.core.mail import send_mail
import datetime

class Command(BaseCommand):
    help = 'List certificates that are to be expired the upcoming month ' \
           'list the Luipaard clusters which are queried'

    def handle(self, *args, **kwargs):

        #string waarin alle certificaten worden opgenomen welke gaan verlopen
        mail_body_certs_30dgn = ''
        mail_body_bigip_nodes = ''
        mail_body_certs_serverssl_30dgn = ''
        counter = 0

        for cert_client_ssl in CertClientSSLVirtualServer.objects.all():
            self.stdout.write(cert_client_ssl.cert_name)

            # test of het certificaat van de virtual server niet al verlopen is en of de verloopdatum niet meer dan een maand later is
            if datetime.date.today() < cert_client_ssl.cert_expiration.date() \
                    and (cert_client_ssl.cert_expiration.date() - datetime.date.today() < datetime.timedelta(days=400)):

                mail_body_certs_30dgn += '\n' \
                                         + 'virtual server: ' + cert_client_ssl.vs_name \
                                         + ', op luipaardcluster: ' + cert_client_ssl.cert_cluster \
                                         + ', in partition: ' + cert_client_ssl.vs_partition \
                                         + ', met ssl client profile: ' + cert_client_ssl.cssl_name \
                                         + ', en certificaat: ' + cert_client_ssl.cert_name \
                                         + ', verloopt op: ' + str(cert_client_ssl.cert_expiration.date().strftime("%d %b %Y %H:%M:%S")) \
                                         + '\n'

            else:
                continue

        for cert_server_ssl in CertServerSSLVirtualServer.objects.all():
            self.stdout.write(cert_server_ssl.cert_name)

            # test of het certificaat van de virtual server niet al verlopen is en of de verloopdatum niet meer dan een maand later is
            if datetime.date.today() < cert_server_ssl.cert_expiration.date() \
                    and (cert_server_ssl.cert_expiration.date() - datetime.date.today() < datetime.timedelta(days=400)):

                mail_body_certs_serverssl_30dgn += '\n' \
                                         + 'virtual server: ' + cert_server_ssl.vs_name \
                                         + ', op luipaardcluster: ' + cert_server_ssl.cert_cluster \
                                         + ', in partition: ' + cert_server_ssl.vs_partition \
                                         + ', met ssl server profile: ' + cert_server_ssl.server_ssl_name \
                                         + ', en certificaat: ' + cert_server_ssl.cert_name \
                                         + ', verloopt op: ' + str(cert_server_ssl.cert_expiration.date().strftime("%d %b %Y %H:%M:%S")) \
                                         + '\n'

            else:
                continue

        #overzicht van de clusters waarvoor het certificaatoverzicht is gemaakt.

        for node in Database.objects.all().select_related():
            #print(str(node.created_on.strftime("%d %b %Y %H:%M:%S")))
            mail_body_bigip_nodes += '\n' \
                                     + str(node.bigip_name) \
                                     + ' (db update: ' + str(node.created_on.strftime("%d %b %Y %H:%M:%S")) + ')'

        mail_body = "Hoi AS&D team," \
                    + '\n \n' \
                    + "Dit geautomatiseerde bericht geeft een overzicht van certificaten (op basis van zowel client als server SSL profielen) welke de komende 30 dagen gaan verlopen. " \
                    + "Het betreft certificaten op de clusters: "\
                    + '\n' + mail_body_bigip_nodes \
                    + '\n \n' \
                    + "De volgende client SSL profile certificaten verlopen de komende 30 dagen: " \
                    + '\n ' \
                    + mail_body_certs_30dgn \
                    + '\n \n' \
                    + "De volgende server SSL profile certificaten verlopen de komende 30 dagen: " \
                    + '\n ' \
                    + mail_body_certs_serverssl_30dgn \
                    + '\n \n' \
                    + "Met vriendelijke groeten van de wi104366.ciman.nl" \
                    + '\n \n' \

        mail_subject_date = datetime.date.today() + datetime.timedelta(days=7)

        mail_subject = 'AS&D certificaatverloopdata - volgende update volgt op: ' + str(mail_subject_date)

        print(mail_body)

        #send_mail(mail_subject, mail_body, 'mailadres')
