from django.db import models

class IrulesNotAssigned(models.Model):
    irule_name = models.CharField(max_length=200)
    irule_cluster = models.CharField(max_length=200)

    class Meta:
        ordering = ['irule_cluster']

    def __str__(self):
        return self.irule_name