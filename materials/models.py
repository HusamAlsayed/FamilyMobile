from django.db import models

# Create your models here.
from user.models import CustomUser


class Material(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    is_service = models.BooleanField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)


class OutlayType(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)


class Outlay(models.Model):
    price = models.FloatField()
    date = models.DateField(auto_now=True)
    description = models.CharField(max_length=100)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    outlay_type = models.ForeignKey(OutlayType, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
