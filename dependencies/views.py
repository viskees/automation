from django.shortcuts import render

# Create your views here.

from django.shortcuts import render

# Create your views here.

def dependencies(request):
    context = {}
    return render(request, 'dependencies/dependencies.html', context)