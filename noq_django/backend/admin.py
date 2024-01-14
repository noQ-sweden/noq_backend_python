from django.contrib import admin

from .models import Host, Reservation, User, Product, ProductRule, ProductBooking 

admin.site.register(Host)
admin.site.register(Reservation)
admin.site.register(User)
admin.site.register(Product)
admin.site.register(ProductRule)
admin.site.register(ProductBooking)
