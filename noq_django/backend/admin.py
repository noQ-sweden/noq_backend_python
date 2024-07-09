from django.contrib import admin

from .models import Host, Client, Product, Region, Booking, Available, Invoice

# admin.site.register(Host)
# admin.site.register(Available)
# admin.site.register(User)
# admin.site.register(Product)
admin.site.register(Region)
# admin.site.register(Booking)


@admin.register(Client)
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
    list_display = ("start_date", "end_date", "user", "product")
    list_filter = ("start_date", "end_date", "product")
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


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'host', 'amount', 'created_at', 'due_date', 'paid', 'currency')
    list_filter = ('paid', 'created_at', 'host', 'currency')
    search_fields = ('id', 'host__name', 'description', 'invoice_number')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    fields = ('host', 'amount', 'description', 'paid', 'due_date', 'currency', 'invoice_number')
    readonly_fields = ('created_at', 'updated_at')