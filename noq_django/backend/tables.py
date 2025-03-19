# tables.py

import django_tables2 as tables
from .models import Booking, Available


class AvailableProducts(tables.Table):
    boka = tables.TemplateColumn('<a href="{{record.url}}/book/{{record.pk}}">Boka</a>')
    # boka = tables.TemplateColumn('<a href="{{record.url}}">{{record.name}}</a>')
    pause = 5

    class Meta:
        model = Available
        fields = ("product", "places_left", "boka")
