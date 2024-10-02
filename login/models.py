from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):  
    tema = models.CharField(max_length=10, default='claro')
    roles= models.CharField(max_length=20,default=None, null=True)#Quitar que permite nulos
    num_control = models.IntegerField(unique=True,default=None, null=True) 