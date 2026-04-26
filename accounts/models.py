from django.db import models

class RegUser(models.Model):
    full_name = models.CharField(max_length=100, blank=False)
    username = models.CharField(max_length=100, unique=True, blank=False)
    email = models.EmailField(max_length=100, unique=True, blank=False)
    password = models.CharField(max_length=100, blank=False)
    phone_number = models.CharField(max_length=10, blank=False)
    status = models.CharField(default='waiting', max_length=20)

    def __str__(self):
        return self.username
