from django.db import models

# Create your models here.

from django.db import models

# Create your models here.

class BigIPNodes(models.Model):
    bigip_name = models.CharField(max_length=200)
    bigip_ip = models.CharField(max_length=15)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.bigip_name

class Database(models.Model):
    bigip_name = models.ForeignKey(BigIPNodes, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)

class Certificates(models.Model):
    bigip_name = models.ForeignKey(BigIPNodes, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    partition = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    expiration = models.DateTimeField()

    def __str__(self):
        return self.name

class ProfileSSLClient(models.Model):
    bigip_name = models.ForeignKey(BigIPNodes, on_delete=models.CASCADE)
    certificate = models.ForeignKey(Certificates, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    partition = models.CharField(max_length=200)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class VirtualServer(models.Model):
    bigip_name = models.ForeignKey(BigIPNodes, on_delete=models.CASCADE)
    profilesslclient = models.ForeignKey(ProfileSSLClient, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    partition = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)

    def __str__(self):
        return self.name