from django.db import models

# Create your models here.
from django.db import models
from database.models import *

# Create your models here.

class BigIPNodePartionCheck(models.Model):
    bigip_name = models.ForeignKey(BigIPNodes, on_delete=models.CASCADE)
    partition_name = models.CharField(max_length=15)
    partition_size = models.CharField(max_length=15)
    partition_previous_size = models.CharField(max_length=15)

    def __str__(self):
        return self.bigip_name