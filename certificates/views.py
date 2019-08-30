from django.shortcuts import render

# Create your views here.

def certificates(request):
    context = {}
    return render(request, 'certificates/certificates.html', context)