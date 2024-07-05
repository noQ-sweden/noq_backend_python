import sys
sys.path.append("....backend") # Adds folder where backend is to python modules path.
import json
from datetime import datetime, timedelta
from django.test import TestCase
from django.contrib.auth.models import User, Group
from backend.models import Host, Client, Product, Region, Booking, State, BookingStatus
from django.test import Client as TestClient
from ..host_api import router

class TestHostFrontpageApi(TestCase):
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

        # Login the host user
        self.client = TestClient(router)
        self.client.login(username=self.host_name, password=self.password)


    def delete_users(self):
        # Delete the host_user created for the tests
        users = User.objects.all()
        users.delete()


    def delete_products(self):
        # Delete all products created for the tests
        Product.objects.all().delete()
        Host.objects.all().delete()
        Region.objects.all().delete()


    def setUp(self):
        # log in host user for the tests
        self.host_login()

        # Create products that can be used during the tests
        if Product.objects.filter(id=1).first() == None:
            region = Region.objects.create(name="Malmö")
            hostA = Host.objects.create(name="Host 1", street="", postcode="", city="Malmö", region_id=region.id)
            hostB = Host.objects.create(name="Host 2", street="", postcode="", city="Malmö", region_id=region.id)
            productA = Product.objects.create(name="room", total_places=2, host_id=hostA.id, type="room")
            productB = Product.objects.create(name="room", total_places=5, host_id=hostB.id, type="room")
            productC = Product.objects.create(name="room", total_places=3, host_id=hostB.id, type="room")

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

    def test_get_host_info(self):
        # Connect host_user and host
        host = Host.objects.get(id=1)
        host_user = User.objects.get(username=self.host_name)
        host.users.add(host_user)
        host.save()

        response = self.client.get("/api/host/")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['name'], "Host 1")


    def test_get_host_info_no_host(self):
        response = self.client.get("/api/host/")

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(data['detail'], "User is not admin to a host.")


    def test_get_available_places_host(self):
        # Connect host_user and host
        host = Host.objects.get(name="Host 2")
        host_user = User.objects.get(username="user.host@test.nu")
        host.users.add(host_user)
        host.save()

        # Get products that will be booked, Host 2 has two products
        products = Product.objects.filter(host_id=host).all()
        clients = Client.objects.all()

        current_date = datetime.now().date()
        # Add bookings for the client_user (brukare)
        for i in range(6):
            # 5 bookings for today, 1 for tomorrow
            extra_day = 1 if i > 3 else 0
            # 3 bookings for product 1, 3 bookings for product 2, 2 for next day
            product_idx = 1 if i > 2 else 0
            Booking.objects.create(
                start_date=current_date + timedelta(days=extra_day),
                product=products[product_idx],
                user=clients[i % 4],
                status=BookingStatus.objects.create(description="reserved"),
            )
        bookings = Booking.objects.all()
        # Get availability for two days
        response = self.client.get("/api/host/available/2")

        self.assertEqual(response.status_code, 200)

        tomorrows_date = current_date + timedelta(days=1)
        data = json.loads(response.content)
        # 3 places booked from 1st product
        self.assertEqual(data[str(current_date)][0]['places_left'], 2)
        self.assertEqual(data[str(current_date)][1]['places_left'], 2)
        # 1 place booked from 1st product
        self.assertEqual(data[str(tomorrows_date)][0]['places_left'], 5)
        self.assertEqual(data[str(tomorrows_date)][1]['places_left'], 1)


    def tearDown(self):
        # After the tests delete all data generated for the tests
        self.delete_products()
        self.delete_users()