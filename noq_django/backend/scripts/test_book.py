import random
from datetime import datetime, timedelta
from icecream import ic
from faker import Faker

from backend.models import Host, UserDetails, Product, Region, Booking, Available


def add_product_bookings(product_id: int, user: UserDetails, days_ahead: int = 10):
    print("\n---- PRODUCT BOOKINGS ----")

    print(f"Bokning av {user.first_name} {user.last_name}")
    booking = Booking(
        start_date=datetime.now() + timedelta(days_ahead),
        product=Product.objects.get(id=product_id),
        user=user,
    )

    try:
        booking.save()
        exceptions = 0
    except Exception as ex:
        print(ex)
    else:
        print("Booking added")


def booking_list(product_id: int, days_ahead: int = 10):
    start_date = datetime.now() + timedelta(days_ahead)
    bookings = Booking.objects.filter(product_id=product_id, start_date=start_date)

    for booking in bookings:
        ic(booking)


def available_list(product_id: int, days_ahead: int = 10):
    start_date = datetime.now() + timedelta(days_ahead)

    available = Available.objects.filter(
        product_id=product_id, available_date=start_date
    )
    ic(available)


def book_product(product_id: int = 0, days_ahead: int = 10):
    datum = datetime.now() + timedelta(days_ahead)
    if product_id == 0:
        product = Product.objects.first()
    else:
        product = Product.objects.filter(pk=product_id).first()

    if not product:
        raise Exception("Product not found: " + product_id)

    print(product)
    # print(f'{product.description} [{product.id}]')

    users = UserDetails.objects.all()
    for user in users:
        if not UserDetails.objects.filter(start_date=datum):
            continue
        if not Booking.objects.filter(
            product_id=product_id, user_id=user.id, start_date=datum
        ):
            break

    # ic(user)

    available_list(product.id)
    add_product_bookings(product_id=product.id, user=user)
    booking_list(product.id)
    available_list(product.id)


def run(*args):
    docs = """
    test_book
    
    python manage.py runscript test_book 
    
    Args: [--script-args product_id]
    
    """

    if len(args) > 0:
        product_id = int(args[0])
    else:
        product_id = 0

    print("product_id:", product_id)
    book_product(product_id)
    # available_list()
