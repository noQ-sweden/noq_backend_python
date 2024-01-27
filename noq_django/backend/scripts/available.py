import random
from datetime import datetime, timedelta, date
from icecream import ic
from faker import Faker

from backend.models import Host, UserDetails, Product, Region, Booking, Available


def count_bookings(product: Product, datum: datetime):
    bookings_count = Booking.objects.filter(product=product, start_date=datum).count()
    return bookings_count


def add_available(days_ahead) -> int:
    n = 0
    datum = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
    places_left = 5
    for product in Product.objects.all():
        places_left = product.total_places - count_bookings(product, datum)

        if not Available.objects.filter(product=product):
            avail = Available.objects.create(
                available_date=datum, product=product, places_left=places_left
            )
            n += 1
    return n


def available():
    print("Tillgängliga platser de närmaste dagarna:")
    last_date = datetime.now()  # .timedelta(days=1)
    print("\n\t" + last_date.strftime("%Y-%m-%d"))
    for avail in Available.objects.filter(available_date=last_date).all():
        print(
            f"\t\t{avail.places_left} platser kvar på {avail.product.description} på {avail.product.host.name} {avail.product.host.street}"
        )

    last_date = datetime.now() + timedelta(days=1)
    print("\n\t" + last_date.strftime("%Y-%m-%d"))
    for avail in Available.objects.filter(available_date=last_date).all():
        print(
            f"\t\t{avail.places_left} platser kvar på {avail.product.description} på {avail.product.host.name} {avail.product.host.street}"
        )


def run():
    added = add_available(0) + add_available(1) + add_available(2)
    print(added)
    available()
