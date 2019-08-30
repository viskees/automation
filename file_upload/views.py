from django.shortcuts import render

from django.core.files.storage import FileSystemStorage

# Create your views here.

def file_upload(request):
    print(request)
    if request.method == 'POST' and request.FILES['file']:
        myfile = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        return render(request, 'file_upload/file_upload.html', {
            'uploaded_file_url': uploaded_file_url
        })
    return render(request, 'file_upload/file_upload.html')