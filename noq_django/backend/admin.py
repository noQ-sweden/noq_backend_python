from django.contrib import admin

from .models import Host, UserDetails, Product, Region, Booking, Available

# admin.site.register(Host)
# admin.site.register(Available)
# admin.site.register(User)
# admin.site.register(Product)
admin.site.register(Region)
# admin.site.register(Booking)


@admin.register(UserDetails)
class UserAdmin(admin.ModelAdmin):
    fields = (("first_name", "last_name"), "gender", "street", ("postcode", "city"), "region")
    list_display = ("first_name", "last_name", "gender", "street", "city", "region")
    list_filter = ("city","region")
    ordering = ("first_name",)
    search_fields = ("first_name",)


@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    list_display = ("name", "street", "postcode", "city", "region")
    list_filter = ("city","region")
    ordering = ("name",)
    search_fields = ("name",)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("start_date", "user", "product")
    list_filter = ("start_date","product")
    ordering = ("start_date",)
    search_fields = ("start_date",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("description", "host", "name", "total_places", "type")
    list_filter = ("host","total_places")
    ordering = ("description",)
    search_fields = ("description",)


@admin.register(Available)
class AvailableAdmin(admin.ModelAdmin):
    list_filter = ("available_date","places_left")
    list_display = ("available_date", "places_left", "product")
    ordering = ("available_date",)
    search_fields = ("available_date",)
