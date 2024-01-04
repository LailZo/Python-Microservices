# myproject/models.py

from django.db import models


class Order(models.Model):
    user_id = models.CharField(max_length=255)
    product_code = models.CharField(max_length=255)
    customer_fullname = models.CharField(max_length=255, blank=True, null=True)
    product_name = models.CharField(max_length=255, blank=True, null=True)
    total_amount = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
