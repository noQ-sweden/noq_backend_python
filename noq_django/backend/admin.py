from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Host, Client, Product, Region, Booking, Available, Invoice, InvoiceStatus


class CaseworkerGroupFilter(admin.SimpleListFilter):
    title = "Caseworker" #Displayed title in the admin filter sidebar
    parameter_name = "caseworker" # name of the filter

    def lookups(self, request, model_admin):
        try:
            # Return a list od caseworkers (filtered by the 'caseworker' group)
            caseworker_group = Group.objects.get(name='caseworker')
            caseworkers = caseworker_group.user_set.all()
            return [(user.id, f'{user.first_name} {user.last_name}') for user in caseworkers] 
        except Group.DoesNotExist:
            return []

    def queryset(self, request, queryset):
        # Filter host by the selected caseworkerfrom the list
        if self.value():
            return queryset.filter(caseworkers__id=self.value())
        return queryset

# defining inline admin descriptior for the caseworkers relationship
class CaseworkerInline(admin.TabularInline):
    model = Host.caseworkers.through
    extra = 1


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    fields = (("first_name", "last_name"), "gender", "street", ("postcode", "city"), "region")
    list_display = ("first_name", "last_name", "gender", "street", "city", "region")
    list_filter = ("city","region")
    ordering = ("first_name",)
    search_fields = ("first_name",)


@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    list_display = ("name", "street", "postcode", "city", "region")
    list_filter = ("city","region", CaseworkerGroupFilter) #Using the custum filter 
    ordering = ("name",)
    search_fields = ("name", "caseworkers__first_name")

    # Exclude the 'caseworkers' field from the main form, as it's being handled by inline
    exclude = ("caseworkers",)

    # add the CaseworkerInline to allow editing caseworkers in the admin interface
    inlines = [CaseworkerInline]


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
    list_display = ('id', 'host', 'amount', 'vat', 'vat_rate', 'created_at', 'due_date', 'status', 'currency', 'invoice_number')
    list_filter = ('status', 'created_at', 'host', 'currency', 'vat_rate')
    search_fields = ('id', 'host__name', 'description', 'invoice_number', 'buyer_name', 'buyer_vat_number', 'seller_vat_number')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    fields = ('host', 'amount', 'vat', 'vat_rate', 'description', 'status', 'due_date', 'currency', 'invoice_number', 'sale_date', 'seller_vat_number', 'buyer_vat_number', 'buyer_name', 'buyer_address')
    readonly_fields = ('created_at', 'updated_at')

    actions = ['recalculate_vat']
    def recalculate_vat(self, request, queryset):
        for invoice in queryset:
            invoice.calculate_vat()
            invoice.save()
        self.message_user(request, "VAT has been recalculated for selected invoices.")

    recalculate_vat.short_description = "Recalculate VAT for selected invoices"

    def calculate_vat(self, obj):
        return (obj.amount * obj.vat_rate) / 100 if obj.vat_rate else 0
    calculate_vat.short_description = 'Calculated VAT'



@admin.register(InvoiceStatus)
class InvoiceStatusAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
    search_fields = ('name',)
