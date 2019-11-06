from django.core.mail import send_mail

from django.conf import settings

def sendmail_configure():
    settings.configure(EMAIL_HOST = 'smtp.t-mobilethuis.nl', EMAIL_PORT = 25)

#EMAIL_USE_TLS = 'False'
#EMAIL_HOST_USER = 'viskees@t-mobilethuis.nl'
#EMAIL_HOST_PASSWORD = '')

sendmail_configure()

send_mail('subject', 'body', 'viskees@t-mobilethuis.nl', ['viskees@gmail.com'])