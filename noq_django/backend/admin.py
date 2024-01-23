from django.contrib import admin

from .models import Host, User, Product, Region, Booking, Available

admin.site.register(Host)
admin.site.register(Available)
admin.site.register(User)
admin.site.register(Product)
admin.site.register(Region)
admin.site.register(Booking)
