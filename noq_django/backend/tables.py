# tables.py

import django_tables2 as tables
from .models import ProductBooking


class AvailableProducts(tables.Table):
    boka = tables.TemplateColumn('<a href="{{record.url}}">{{record.name}}</a>')

    class Meta:
        model = ProductBooking
        fields = ("product", "user", "boka")
