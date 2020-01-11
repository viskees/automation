from django.core.management.base import BaseCommand
from database.models import *
from django.core.mail import send_mail
import datetime

class Command(BaseCommand):
    help = 'List certificates that are to be expired the upcoming month ' \
           'List the top 10 to be expired certificates' \
           'list the Luipaard clusters which are queried'

    def handle(self, *args, **kwargs):

        #string waarin alle certificaten worden opgenomen die gaan verlopen
        mail_body_certs_30dgn = ''
        mail_body_certs_top10 = ''
        mail_body_bigip_nodes = ''
        counter = 0

        for virtual_server in VirtualServer.objects.select_related().order_by('profilesslclient__certificate__expiration').filter(profilesslclient_id__isnull=False):
            #self.stdout.write(virtual_server.name)

            #test of het certificaat van de virtual server niet al verlopen is en of de verloopdatum niet meer dan een maand later is
            if datetime.date.today() < virtual_server.profilesslclient.certificate.expiration.date() \
                    and (virtual_server.profilesslclient.certificate.expiration.date() - datetime.date.today() < datetime.timedelta(days=30) ):

                mail_body_certs_30dgn += '\n' \
                             + 'virtual server: ' + virtual_server.name \
                             + ', op luipaardcluster: ' + virtual_server.bigip_name.bigip_name \
                             + ', in partition: ' + virtual_server.partition \
                             + ', met ssl client profile: ' +  virtual_server.profilesslclient.name \
                             + ', en certificaat: ' + virtual_server.profilesslclient.certificate.name \
                             + ', verloopt op: ' + str(virtual_server.profilesslclient.certificate.expiration.strftime("%d %b %Y %H:%M:%S")) \
                             + '\n'
            elif datetime.date.today() < virtual_server.profilesslclient.certificate.expiration.date() and counter < 10:

                mail_body_certs_top10 += '\n' \
                             + 'virtual server: ' + virtual_server.name \
                             + ', op luipaardcluster: ' + virtual_server.bigip_name.bigip_name \
                             + ', in partition: ' + virtual_server.partition \
                             + ', met ssl client profile: ' + virtual_server.profilesslclient.name \
                             + ', en certificaat: ' + virtual_server.profilesslclient.certificate.name \
                             + ', verloopt op: ' + str(virtual_server.profilesslclient.certificate.expiration.strftime("%d %b %Y %H:%M:%S")) \
                             + '\n'

                counter += 1

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
                    + "Dit geautomatiseerde bericht geeft een overzicht van certificaten (op basis van client SSL profielen) welke de komende periode gaan verlopen. " \
                    + "Het betreft certificaten op de clusters: "\
                    + '\n' + mail_body_bigip_nodes \
                    + '\n \n' \
                    + "De volgende certificaten verlopen de komende 30 dagen: " \
                    + '\n ' \
                    + mail_body_certs_30dgn \
                    + '\n \n' \
                    + "Een top 10 overzicht van certificaten die de komende tijd gaan verlopen: " \
                    + '\n ' \
                    + mail_body_certs_top10 \
                    + '\n \n' \
                    + "Met vriendelijke groeten van de wi104366.ciman.nl" \
                    + '\n \n' \

        mail_subject_date = datetime.date.today() + datetime.timedelta(days=7)

        mail_subject = 'AS&D certificaatverloopdata - volgende update volgt op: ' + str(mail_subject_date)

        #print(mail_body)

        send_mail(mail_subject, mail_body, 'DictuCloudASD@dictu.nl', ['DictuCloudASD@dictu.nl', 'd.eshuis@dictu.nl', 'r.bakker@dictu.nl'])
