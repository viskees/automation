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
        mail_body = ''
        counter = 0

        for virtual_server in VirtualServer.objects.select_related().order_by('profilesslclient__certificate__expiration').filter(profilesslclient_id__isnull=False):
            #self.stdout.write(virtual_server.name)

            #test of het certificaat van de virtual server niet al verlopen is en of de verloopdatum niet meer dan een maand later is
            if datetime.date.today() < virtual_server.profilesslclient.certificate.expiration.date() \
                    and (virtual_server.profilesslclient.certificate.expiration.date() - datetime.date.today() < datetime.timedelta(days=30) ):

                mail_body += 'De komende maand verlopen de volgende certificaten: ' \
                             + '\n' \
                             + 'virtual server: ' + virtual_server.name \
                             + ', op luipaardcluster: ' + virtual_server.bigip_name.bigip_name \
                             + ', in partition: ' + virtual_server.partition \
                             + ', met ssl client profile: ' +  virtual_server.profilesslclient.name \
                             + ', en certificaat: ' + virtual_server.profilesslclient.certificate.name \
                             + ', verloopt op: ' + str(virtual_server.profilesslclient.certificate.expiration) \
                             + '\n'
            elif datetime.date.today() < virtual_server.profilesslclient.certificate.expiration.date() and counter < 10:

                mail_body += 'De volgende 10 certificaten gaan als eerste verlopen: ' \
                             + '\n' \
                             + 'virtual server: ' + virtual_server.name \
                             + ', op luipaardcluster: ' + virtual_server.bigip_name.bigip_name \
                             + ', in partition: ' + virtual_server.partition \
                             + ', met ssl client profile: ' + virtual_server.profilesslclient.name \
                             + ', en certificaat: ' + virtual_server.profilesslclient.certificate.name \
                             + ', verloopt op: ' + str(virtual_server.profilesslclient.certificate.expiration) \
                             + '\n'

            else:
                continue

        print(mail_body)
        #send_mail('subject', mail_body, 'viskees@t-mobilethuis.nl', ['viskees@gmail.com'])