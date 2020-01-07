from django.db import models

# Create your models here.

class CertClientSSLVirtualServer(models.Model):
    cert_name  = models.CharField(max_length=200)
    cert_partition = models.CharField(max_length=200)
    cert_expiration = models.DateTimeField()
    cert_cluster = models.CharField(max_length=200)
    cssl_name = models.CharField(max_length=200)
    cssl_partition = models.CharField(max_length=200)
    vs_name = models.CharField(max_length=200)
    vs_partition = models.CharField(max_length=200)
    vs_ip = models.CharField(max_length=200)

    class Meta:
        ordering = ['cert_expiration']

    def __str__(self):
        return self.cert_name