import sys
sys.path.append("....backend")
from django.db.models import Q
from django.contrib.auth.models import User, Group
from backend.models import (Host, Client, Product, Region, Booking,
                            Available, State, BookingStatus)
from django.test import Client as TestClient
from datetime import datetime, timedelta
from ..host_api import router

class TestData():
    test_client = None
    user = None
    client = None
    usernames = ["user.one@test.nu", "user.two@test.nu"]
    password = "userpassword"
    users = []
    hosts = []
    products = []
    region = None

    def __init__(self):
        # Create table for booking statuses
        self.add_booking_statuses()
        # Add product data
        self.add_product_data()
        # Count availability for a week
        for product in Product.objects.all():
            self.calc_available(product)



    def user_login(self, user_group, nr_of_users):
        if nr_of_users > len(self.usernames) or nr_of_users < 1:
            message = ("Error: Can't create " + str(nr_of_users)
                       + " users. Value has to be between 1 and "
                       + str(len(self.usernames)))
            raise Exception(message)

        # Create users for the tests if not existing
        if User.objects.filter(username=self.usernames[0]).first() == None:
            for i in range(nr_of_users):
                user = User.objects.create_user(
                    username=self.usernames[i], password=self.password)
                group_obj, created = Group.objects.get_or_create(name=user_group)
                user.groups.add(group_obj)
                self.users.append(user)
                client = Client.objects.create(
                    first_name=user.username,
                    gender="K",
                    user=user,
                    region=self.region)

        # Login the first user
        self.test_client = TestClient(router)
        self.test_client.login(
            username=self.usernames[0], password=self.password)


    def create_clients(self, users, region):
        for user in self.users:
            # All clients are women so all products can be booked by
            # every client
            client = Client.objects.create(
                first_name=user.username, gender="K", user=user, region=region)


    def add_booking_statuses(self):
        statuses = [
            {"id": State.PENDING, "description": "pending"},
            {"id": State.DECLINED, "description": "declined"},
            {"id": State.ACCEPTED, "description": "accepted"},
            {"id": State.CHECKED_IN, "description": "checked_in"},
            {"id": State.IN_QUEUE, "description": "in_queue"},
            {"id": State.RESERVED, "description": "reserved"},
            {"id": State.CONFIRMED, "description": "confirmed"},
        ]

        for status in statuses:
            if not BookingStatus.objects.filter(id=status["id"]).exists():
                booking_status = BookingStatus.objects.create(
                    id=status["id"], description=status["description"]
                )
                booking_status.save()


    def add_product_data(self):
        # Create products that can be used during the tests
        if Product.objects.filter(id=1).first() == None:
            # Create a region
            self.region = Region.objects.create(name="Malmö")

            # Create two hosts
            hostA = Host.objects.create(
                name="Host A",
                street="Bennets Väg 9",
                postcode="21367",
                city="Malmö",
                region_id=self.region.id
            )
            self.hosts.append(hostA)

            hostB = Host.objects.create(
                name="Host B",
                street="Idunavägen 11",
                postcode="21619",
                city="Malmö",
                region_id=self.region.id
            )
            self.hosts.append(hostB)

            # Create four general products, two for each host and
            # one woman-only product for HostA
            for i in range(4):
                nr_of_places = 2 * (i + 1)
                host_id = hostA.id if i < 2 else hostB.id
                product = Product.objects.create(
                    name="room",
                    total_places=nr_of_places,
                    host_id=host_id,
                    type="room"
                )
                self.products.append(product)

            product = Product.objects.create(
                name="woman-only",
                total_places=1,
                host_id=hostA.id,
                type="woman-only"
            )
            self.products.append(product)


    def bookings_count_per_date(self, product):
        # Return count for bookings for one week including current date
        start_date = datetime.now().date()
        time_period_in_days = 7
        booking_counts = {}

        for i in range(time_period_in_days):
            date_time = start_date + timedelta(days=i)
            count = Booking.objects.filter(
                Q(product=product)
                & Q(start_date__lte=date_time)
                & Q(end_date__gt=date_time)
                & ~Q(status=State.DECLINED)
                & ~Q(status=State.IN_QUEUE)
            ).count()
            date = f"{date_time:%Y-%m-%d}"
            booking_counts[date] = count

        return booking_counts


    def calc_available(self, product):
        bookings_per_day = self.bookings_count_per_date(product)
        for date in bookings_per_day:
            places_left = product.total_places - bookings_per_day[date]

            existing_availability = Available.objects.filter(
                product=product, available_date=date
            ).first()

            if existing_availability:
                existing_availability.places_left = places_left
                existing_availability.save()
            else:
                product_available = Available(
                    available_date=date,
                    product=Product.objects.get(id=product.id),
                    places_left=places_left,
                )
                product_available.save()


    def delete_users(self):
        User.objects.all().delete()


    def delete_products(self):
        # Delete all products created for the tests
        Product.objects.all().delete()
        Available.objects.all().delete()
        Host.objects.all().delete()
        Region.objects.all().delete()
