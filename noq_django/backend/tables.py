# tables.py

import django_tables2 as tables
from .models import ProductBooking


class AvailableProducts(tables.Table):
    class Meta:
        model = ProductBooking
        fields = ("product", "user")
