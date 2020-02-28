from django.db import models

# Create your models here.

from django.db import models

# Create your models here.


class BigIPNodes(models.Model):
    bigip_name = models.CharField(max_length=200)
    bigip_ip = models.CharField(max_length=15)

    def __str__(self):
        return self.bigip_name


class Database(models.Model):
    bigip_name = models.ForeignKey(BigIPNodes, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.bigip_name


class Certificates(models.Model):
    bigip_name = models.ForeignKey(BigIPNodes, on_delete=models.CASCADE)
    partition = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    full_name = models.CharField(max_length=200)
    expiration = models.DateTimeField()
    commonName = models.CharField(max_length=200)
    certificateKeySize = models.CharField(max_length=200)
    publicKeyType = models.CharField(max_length=200)
    organization = models.CharField(max_length=200)
    ou = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    subjectAlternativeName = models.CharField(max_length=2048)

    class Meta:
        ordering = ['bigip_name']

    def __str__(self):
        return self.name


class ProfileSSLClient(models.Model):
    bigip_name = models.ForeignKey(BigIPNodes, on_delete=models.CASCADE)
    certificates = models.ManyToManyField(Certificates)
    full_name = models.CharField(max_length=200)
    partition = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    cert_names = models.TextField()

    class Meta:
        ordering = ['bigip_name']

    def __str__(self):
        return self.name


class ProfileSSLServer(models.Model):
    bigip_name = models.ForeignKey(BigIPNodes, on_delete=models.CASCADE)
    certificate = models.ForeignKey(Certificates, on_delete=models.CASCADE, null=True)
    full_name = models.CharField(max_length=200)
    partition = models.CharField(max_length=200)
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ['bigip_name']

    def __str__(self):
        return self.name


class Datagroup(models.Model):
    bigip_name = models.ForeignKey(BigIPNodes, on_delete=models.CASCADE)
    profile_server_ssl = models.ManyToManyField(ProfileSSLServer)
    full_name = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    partition = models.CharField(max_length=200)
    datagroup_profile_server_ssl = models.CharField(max_length=200)
    #key_values = models.TextField()

    class Meta:
        ordering = ['bigip_name']

    def __str__(self):
        return self.name


class Irule(models.Model):
    bigip_name = models.ForeignKey(BigIPNodes, on_delete=models.CASCADE)
    datagroup = models.ManyToManyField(Datagroup)
    full_name = models.CharField(max_length=200)
    partition = models.CharField(max_length=200)
    irule_content = models.TextField()
    datagroups = models.CharField(max_length=200)

    class Meta:
        ordering = ['bigip_name']

    def __str__(self):
        return self.full_name


class VirtualServer(models.Model):
    bigip_name = models.ForeignKey(BigIPNodes, on_delete=models.CASCADE)
    profile_client_ssl = models.ManyToManyField(ProfileSSLClient)
    profile_server_ssl = models.ManyToManyField(ProfileSSLServer)
    irule = models.ManyToManyField(Irule)
    full_name = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    partition = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    profiles = models.TextField()
    irules = models.TextField()

    class Meta:
        ordering = ['bigip_name']

    def __str__(self):
        return self.name
