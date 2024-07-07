import sys
sys.path.append("....backend")
import json
from django.test import TestCase
from django.db.models import Q
from django.contrib.auth.models import User, Group
from backend.models import (Host, Client, Product, Region, Booking,
                            Available, State, BookingStatus)
from django.test import Client as TestClient
from datetime import datetime, timedelta
from ..host_api import router

class TestProductsApi(TestCase):
    user = None
    client = None
    username = "user.user@test.nu"
    username_two = "user.user.two@test.nu"
    password = "userpassword"

    def user_login(self):
        # Create users for the tests if not existing
        if User.objects.filter(username=self.username).first() == None:
            self.user = User.objects.create_user(
                username=self.username, password=self.password)
            group_obj, created = Group.objects.get_or_create(name="user")
            self.user.groups.add(group_obj)

            self.user = User.objects.create_user(
                username=self.username_two, password=self.password)
            group_obj, created = Group.objects.get_or_create(name="user")
            self.user.groups.add(group_obj)

        # Login the host user
        self.test_client = TestClient(router)
        self.test_client.login(
            username=self.username, password=self.password)


    def create_clients(self, users, region):
        for user in users:
            client = Client.objects.create(
                first_name=user.username, gender="K", user=user, region=region)


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


    def delete_user(self):
        # Delete the user created for the tests
        user = User.objects.get(username=self.username)
        user.delete()


    def delete_products(self):
        # Delete all products created for the tests
        Product.objects.all().delete()
        Available.objects.all().delete()
        Host.objects.all().delete()
        Region.objects.all().delete()


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


    def setUp(self):
        # log in host user for the tests
        self.user_login()
        # Create products that can be used during the tests
        if Product.objects.filter(id=1).first() == None:
            region = Region.objects.create(name="Malmö")

            hostA = Host.objects.create(
                name="Host A",
                street="Bennets Väg 9",
                postcode="21367",
                city="Malmö",
                region_id=region.id
            )
            hostB = Host.objects.create(
                name="Host B",
                street="Idunavägen 11",
                postcode="21619",
                city="Malmö",
                region_id=region.id
            )

            for i in range(4):
                nr_of_places = 2 * (i + 1)
                host_id = hostA.id if i < 2 else hostB.id
                product = Product.objects.create(
                    name="room",
                    total_places=nr_of_places,
                    host_id=host_id,
                    type="room"
                )

            product = Product.objects.create(
                name="woman-only",
                total_places=1,
                host_id=hostA.id,
                type="woman-only"
            )

        # Create client
        users = [
            User.objects.get(username="user.user@test.nu"),
            User.objects.get(username="user.user.two@test.nu")
        ]
        self.create_clients(users, region)


        # Count availability for a week
        for product in Product.objects.all():
            self.calc_available(product)

        # Add booking statuses
        self.add_booking_statuses()


    def test_get_available_products(self):
        # No Bookings, so expects to get five products (3 Host A, 2 Host B)
        current_date = datetime.now().date()
        url = "/api/user/available/" + str(current_date)
        response = self.test_client.get(url)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        count = len(data)
        # API returns a list of hosts and their products, check that we
        # receive data for 2 hosts
        self.assertEqual(count, 2)
        # Host A has 3 products, check that we get 3 products with
        # 2 and 4 and 1 places
        self.assertEqual(data[0]["products"][0]["places_left"], 2)
        self.assertEqual(data[0]["products"][1]["places_left"], 4)
        self.assertEqual(data[0]["products"][2]["places_left"], 1)

        # Host B has 2 products, check that we get 2 products with
        # 6 and 8 places
        self.assertEqual(data[1]["products"][0]["places_left"], 6)
        self.assertEqual(data[1]["products"][1]["places_left"], 8)


    def test_book_a_product_success(self):
        '''
        Create a booking
        '''
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=2)
        product_id = Product.objects.get(total_places=4).id

        data = {
            "start_date": start_date,
            "end_date": end_date,
            "product_id": product_id
        }

        url = "/api/user/request_booking"
        response = self.test_client.post(url, data, content_type='application/json')

        # Check status code is 200 and the status of the booking is pending
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["status"]["description"], "pending")


    def test_book_a_product_full(self):
        '''
        Step 1: Create one booking for product with one places
        Step 2: Create second overlapping booking and get back
                a list of available places per day

        Dates    123456
        Booking1   |-|
        Booking2 |----|
        Expected 00110

        Booking2 is not accepted and API returns list of bookings count
        per day and the max amount of places. End date is not included
        in the list.
        '''
        # Step 1: Create a booking for user 2
        start_date = datetime.now().date() + timedelta(days=2)
        end_date = start_date + timedelta(days=2)
        product = Product.objects.get(total_places=1)

        client = Client.objects.get(
            user=User.objects.get(username="user.user.two@test.nu"))

        booking = Booking(
            start_date=start_date,
            end_date=end_date,
            product=product,
            user=client,
            status=BookingStatus.objects.get(id=State.PENDING)
        )
        booking.save()

        # Step 2: Create second booking that doesn't pass the validation
        # as there is no free rooms available
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=5)
        data = {
            "start_date": start_date,
            "end_date": end_date,
            "product_id": product.id
        }

        url = "/api/user/request_booking"
        response = self.test_client.post(url, data, content_type='application/json')

        # Check status code is 200 and the bookings count matches
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        params = json.loads(data['detail'])

        self.assertEqual(params['nr_or_places'], 1)

        self.assertEqual(
            params['bookings_per_date'][f"{start_date:%Y-%m-%d}"], 0)
        self.assertEqual(
            params['bookings_per_date'][f"{start_date + timedelta(days=1):%Y-%m-%d}"], 0)
        self.assertEqual(
            params['bookings_per_date'][f"{start_date + timedelta(days=2):%Y-%m-%d}"], 1)
        self.assertEqual(
            params['bookings_per_date'][f"{start_date + timedelta(days=3):%Y-%m-%d}"], 1)
        self.assertEqual(
            params['bookings_per_date'][f"{start_date + timedelta(days=4):%Y-%m-%d}"], 0)


    def tearDown(self):
        # After the tests delete all data generated for the tests
        self.delete_user()
        self.delete_products()
