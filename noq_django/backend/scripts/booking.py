import random
from datetime import datetime, timedelta, date
from icecream import ic
from faker import Faker

from backend.models import Host, UserDetails, Product, Region, Booking, Available


def date_list(max: int = 3):
    antal = 0
    books = Booking.objects.order_by("start_date").all()

    last_date = datetime.now()
    for book in books:
        datum = book.start_date

        if antal >= max:
            break

        if datum != last_date:
            antal += 1
            print(book.start_date)
            last_date = datum

            for product in Product.objects.filter(
                description=book.product.description
            ).all():
                print(
                    f"\t{product.description} på {product.host.name} {product.host.street}"
                )
                for booking in (
                    Booking.objects.filter(start_date=datum).order_by("product").all()
                ):
                    print(f"\t\t{booking.user.first_name} {booking.user.last_name}")


def run():
    date_list(3)
