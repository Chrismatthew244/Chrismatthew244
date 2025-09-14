from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=255)
    status = models.CharField(max_length=50)

    def __str__(self):
        return self.name
