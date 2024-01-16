from django.contrib import admin

from .models import Host, Reservation, User, Product, Region, ProductBooking 

admin.site.register(Host)
admin.site.register(Reservation)
admin.site.register(User)
admin.site.register(Product)
admin.site.register(Region)
admin.site.register(ProductBooking)
