from django.db import models

class Query(models.Model):
    domain = models.CharField(max_length=255)
    client_ip = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)

class Address(models.Model):
    query = models.ForeignKey(Query, related_name='addresses', on_delete=models.CASCADE)
    ip = models.GenericIPAddressField()