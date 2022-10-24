from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class CustomUser(AbstractUser):
    bio = models.CharField(max_length=100)
    token = models.TextField()
    parent_user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, blank=True, null=True)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        pass
