import random
from datetime import datetime, timedelta
from icecream import ic
from faker import Faker

from backend.models import Host, Client, Product, Region, Booking, Available


def user_list():
    users = Client.objects.order_by("region").all()
    for user in users:
        bookings = Booking.objects.filter(user=user).order_by("start_date").all()
        print(f"{user.first_name} {user.last_name} in {user.region}")
        if len(bookings) == 0:
            print("\tAldrig bokad")
        else:
            print("\tHar bokat:")
            for booking in bookings:
                print(
                    f"\t\tfrån {booking.start_date} till {booking.end_date}: {booking.product.description} på {booking.product.host.name}, {booking.product.host.street}"
                )


def run():
    user_list()
    # available_list()
