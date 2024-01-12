from django.contrib import admin

from .models import Host, Reservation, User, Room

admin.site.register(Host)
admin.site.register(Reservation)
admin.site.register(User)
admin.site.register(Room)
