from django.shortcuts import render

from database.models import *

from datetime import date

import requests

# Create your views here.

def certificates(request):

    headers = {'Authorization': 'Basic YWRtaW46YWRtaW4=', 'Content-Type': 'application/json'}

    print(request.POST)

    context = {}

    if 'query_db_certs' in request.POST:
        #context = {"query_data": Certificates.objects.all().order_by('expiration')}
        context = {"query_data": VirtualServer.objects.select_related().order_by('profilesslclient__certificate__expiration').filter(profilesslclient_id__isnull=False)}

    elif 'cert' in request.POST:
        colon, cert_name, bigip_id = request.POST['cert'].split(":")
        cert_name, bigip_id_not_needed = cert_name.split(',')
        #print(cert_name)
        context = {'certificate_csr': Certificates.objects.all().filter(name__exact=cert_name, bigip_name_id__exact=bigip_id)}

    elif 'cn' in request.POST:
        bigip_ip = BigIPNodes.objects.all().get(bigip_name__exact=request.POST['bigip_name']).bigip_ip
        create_key_url = 'https://%s/mgmt/tm/sys/crypto/key' % bigip_ip

        #create private key
        #post_data = { "name":':common:' + request.POST['name'] + '.key', "keySize":'2048', "keyType":'rsa-private'}

        #create_key_status_code = requests.post(create_key_url, headers=headers, verify=False, json=post_data).status_code

        # create key and csr in one API call
        post_data = { "name":request.POST['name'] + '.key', "commonName":request.POST['cn'],
                     "keySize":"2048", "keyType":"rsa-private",
                     "options":[{"gen-csr":'csr_' + request.POST['name']}], "organization":request.POST['o'],
                     "ou":request.POST['ou'], "city":request.POST['city'], "subject-alternative-name":request.POST['san']}

        create_key_status_code = requests.post(create_key_url, headers=headers, verify=False,
                                               json=post_data).status_code

        context = { "status_code_key": create_key_status_code}


    return render(request, 'certificates/certificates.html', context)

#json post voor CSR
'''{
	"name": "test_csr.key",
	"commonName": "test_csr.local",
	"keySize":"4096",
	"keyType":"rsa-private",
	"options":[{"gen-csr":"test_csr.local"}],
	"organization":"Labje",
	"ou":"ASD",
	"city":"Assen",
	"state":
	"subject-alternative-name":"DNS:test_csr.local, DNS:www.test_csr.local"
}
'''