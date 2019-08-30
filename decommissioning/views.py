from django.shortcuts import render

# Create your views here.

from django.shortcuts import render

# Create your views here.

def decommissioning(request):
    context = {}
    return render(request, 'decommissioning/decommissioning.html', context)