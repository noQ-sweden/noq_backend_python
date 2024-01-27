import random
from datetime import datetime, timedelta
from icecream import ic
from faker import Faker

from backend.models import Host, UserDetails, Product, Region, Booking, Available


def host_list():
    last_date = datetime.now() - timedelta(days=30)
    last_description = ""
    for host in Host.objects.order_by("-region").all():
        print(f"{host.name}, {host.street} i {host.region}")
        for product in Product.objects.filter(host=host).all():
            bookings = (
                Booking.objects.filter(product=product).order_by("start_date").all()
            )
            # ic(bookings)
            if len(bookings) > 0:
                print(f"\t{product.description}")
                for booking in bookings:
                    if last_date != booking.start_date:
                        print(f"\t\t{booking.start_date}")
                        last_description = ""
                    # if last_description != product.description:
                    #     print(f'\t\t{product.description}')
                    print(f"\t\t\t {booking.user.first_name} {booking.user.last_name}")
                    last_date = booking.start_date
                    last_description = product.description
                print("")


def run():
    host_list()
    # available_list()
