from django.contrib import admin

from .models import Host, User, Product, Region, ProductBooking, ProductAvailable

admin.site.register(Host)
admin.site.register(ProductAvailable)
admin.site.register(User)
admin.site.register(Product)
admin.site.register(Region)
admin.site.register(ProductBooking)
