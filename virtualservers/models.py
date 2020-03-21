from django.db import models

class VirtualServerCluster(models.Model):
    vs_name  = models.CharField(max_length=200)
    vs_ip = models.CharField(max_length=200)
    vs_cluster = models.CharField(max_length=200)

    class Meta:
        ordering = ['vs_cluster']

    def __str__(self):
        return self.vs_name