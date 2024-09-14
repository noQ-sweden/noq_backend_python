import sys
sys.path.append("....backend") # Adds folder where backend is to python modules path.
import json
from datetime import datetime, timedelta
from django.test import TestCase
from django.contrib.auth.models import User, Group
from backend.models import (
    Host, Client, Product, Region, Booking, State, BookingStatus, Available
)
from django.test import Client as TestClient
from ..host_api import router

class TestHostHandleBookingApi(TestCase):
    host_user = None
    host_name = "user.host@test.nu"
    user_name_one = "user.user1@test.nu"
    user_name_two = "user.user2@test.nu"
    user_name_three = "user.user3@test.nu"
    user_name_four = "user.user4@test.nu"
    password = "VeryBadPassword!"

    def create_user(self, username, group):
        user = User.objects.create_user(username=username, password=self.password)
        group_obj, created = Group.objects.get_or_create(name=group)
        user.groups.add(group_obj)

    def host_login(self):
        # Create host user and client users for the test
        if User.objects.filter(username=self.host_name).first() == None:
            host_user = self.create_user(self.host_name, "host")
            client_user_one = self.create_user(self.user_name_one, "user")
            client_user_two = self.create_user(self.user_name_two, "user")
            client_user_three = self.create_user(self.user_name_three, "user")
            client_user_four = self.create_user(self.user_name_four, "user")

        # Login the host
        self.client = TestClient(router)
        self.client.login(username=self.host_name, password=self.password)
        print(self.client)


    def delete_users(self):
        # Delete the host_user created for the tests
        users = User.objects.all().delete()


    def delete_products(self):
        # Delete all products created for the tests
        Product.objects.all().delete()
        Available.objects.all().delete()
        Host.objects.all().delete()
        Region.objects.all().delete()


    def setUp(self):
        # log in host user for the tests
        self.host_login()

        # Create products that can be used during the tests
        if Product.objects.filter(id=1).first() == None:
            region = Region.objects.create(name="Malmö")
            hostA = Host.objects.create(name="Host 1", street="", postcode="", city="Malmö", region_id=region.id)
            productA = Product.objects.create(name="room", total_places=5, host_id=hostA.id, type="room")

        # Create clients
        for i in range(1, 5):
            client = Client.objects.create(
                first_name="John" + str(i),
                last_name="Doe",
                gender="M",
                street="123 Main St",
                postcode="12345",
                city="New York",
                country="USA",
                phone="123-456-7890",
                email="john.doe@example.com",
                unokod="ABC123",
                day_of_birth=datetime.now().date() + timedelta(weeks=-1500),
                personnr_lastnr="1234",
                region=region,
                requirements=None,
                last_edit=datetime.now().date(),
                user=User.objects.get(id=i),
            )

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

        # Create pending bookings
        # 1 product x 4 guests = 4 bookings
        host = Host.objects.get(name="Host 1")
        host_products = Product.objects.filter(host=host)
        clients = Client.objects.all()
        start_date = datetime.now()
        end_date = start_date + timedelta(days=1)

        for product in host_products:
            for guest in clients:
                booking = Booking(
                    start_date=start_date,
                    end_date=end_date,
                    product=product,
                    user=guest,
                    status=BookingStatus.objects.get(
                        id=State.PENDING
                    )
                )
                booking.save()


    def test_bulk_accept_bookings(self):
        # Connect host_user and host
        host = Host.objects.get(name="Host 1")
        host_user = User.objects.get(username="user.host@test.nu")
        host.users.add(host_user)
        host.save()

        # There should be 4 pending bookings to start with
        bookings = Booking.objects.filter(status=State.PENDING).all()
        pending_count = Booking.objects.filter(status=State.PENDING).count()
        self.assertEqual(pending_count, 4)

        # Accept 4 booking in a bulk, there should be 0 pending bookings left
        pending_bookings = Booking.objects.filter(status=State.PENDING).all()
        url = "/api/host/pending/bulk/accept"
        payload = [
            {'booking_id': 1},
            {'booking_id': 2},
            {'booking_id': 3},
            {'booking_id': 4},
        ]

        response = self.client.patch(url, json.dumps(payload), format='json')
        self.assertEqual(response.status_code, 200)
        pending_count = Booking.objects.filter(status=State.PENDING).count()
        self.assertEqual(pending_count, 0)

        # We should get 0 pending bookings via rest api
        response = self.client.get("/api/host/pending")
        self.assertEqual(response.status_code, 200)
        parsed_response = json.loads(response.content)
        self.assertEqual(len(parsed_response), 0)


    def tearDown(self):
        # After the tests delete all data generated for the tests
        self.delete_products()
        self.delete_users()
