from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from django.core.validators import validate_ipv4_address
from django.core.exceptions import ValidationError

# Create your views here.


def decommissioning(request):
    print(request.POST)

    context = {}

    if request.POST:
        print("Het opgegeven IP adres is: " + request.POST['ip_adres'])
        print("Het betreft een " + request.POST['vs_or_node'])

        # form data valideren
        try:
            validate_ipv4_address(request.POST['ip_adres'])
            print("IP is valid: " + request.POST['ip_adres'])
            valid_ip = request.POST['ip_adres']

        except ValidationError:
            print("opgegeven IP is niet valid")
            context = {'validation_error': 'validation_error'}

        # haal virtual server details op


    return render(request, 'decommissioning/decommissioning.html', context)