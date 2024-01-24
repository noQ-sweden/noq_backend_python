import random
from datetime import datetime, timedelta
from icecream import ic
from faker import Faker

from backend.models import Host, User, Product, Region, Booking, Available


def add_product_bookings(product_id: int, user: User, days_ahead: int = 10):

    print("\n---- PRODUCT BOOKINGS ----")
    ic(user)
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

def booking_get(product_id: int, user: User, days_ahead: int = 10):
    start_date=datetime.now() + timedelta(days_ahead)
    
    return Booking.objects.filter(product_id = product_id, user_id=user.id, start_date = start_date)



def booking_list(product_id: int, days_ahead: int = 10):
    start_date=datetime.now() + timedelta(days_ahead)
    
    for booking in Booking.objects.filter(product_id = product_id, start_date = start_date):
        ic(booking)
    
def available_list(product_id: int, days_ahead: int = 10):
    start_date=datetime.now() + timedelta(days_ahead)
    
    
    avail = Available.objects.filter(product_id = product_id, available_date = start_date)
    ic(avail)
    

def add_products():

    product = Product.objects.first()
    ic(product)

    users = User.objects.all()
    for user in users:
        if not booking_get(product_id=product.id, user = user):
            break
        
    ic(user)
    
    available_list(product.id)
    add_product_bookings(product_id=product.id, user=user)
    booking_list(product.id)
    available_list(product.id)
    
    
def run():
    add_products()
    # available_list()
    