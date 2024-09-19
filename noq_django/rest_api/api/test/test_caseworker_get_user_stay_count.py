import sys
sys.path.append("....backend") # Adds folder where backend is to python modules path.
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from backend.models import Region, Host, Product, Client, Booking, BookingStatus, State, Available
from datetime import date, datetime, timedelta
import json
from django.test import Client as TestClient
from ..caseworker_api import router

class TestUserShelterStayCountApi(TestCase):

    caseworker_name = "user.caseworker@test.nu"
    user_name_one = "user.user1@test.nu"
    user_name_two = "user.user2@test.nu"
    password = "VeryBadPassword!"

    def create_user(self, username, group):
        user = User.objects.create_user(username=username, password=self.password)
        group_obj, created = Group.objects.get_or_create(name=group)
        user.groups.add(group_obj)

    def caseworker_login(self):
        if not User.objects.filter(username=self.caseworker_name).exists():
            self.create_user(self.caseworker_name, "caseworker")

        if not User.objects.filter(username=self.user_name_one).exists():
            self.create_user(self.user_name_one, "user")
        if not User.objects.filter(username=self.user_name_two).exists():
            self.create_user(self.user_name_two, "user")

        self.client = TestClient(router)
        self.client.login(username=self.caseworker_name, password=self.password)

    def setUp(self):
        self.caseworker_login()
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
                BookingStatus.objects.create(id=status["id"], description=status["description"])

        if not Region.objects.filter(name="Malmö").exists():
            region = Region.objects.create(name="Malmö")
            hostA = Host.objects.create(name="Host 1", street="", postcode="", city="Malmö", region=region)

        if not Product.objects.filter(name="room").exists():
            productA = Product.objects.create(name="room", total_places=5, host=hostA, type="room")

        region = Region.objects.get(name="Malmö")

        # Client 1 with one booking
        client_one = Client.objects.create(
            first_name="John",
            last_name="Doe",
            gender="M",
            street="123 Main St",
            postcode="12345",
            city="New York",
            country="USA",
            phone="123-456-7890",
            email=self.user_name_one,
            unokod="ABC123",
            day_of_birth=datetime.now().date() + timedelta(weeks=-1500),
            personnr_lastnr="1234",
            region=region,
            requirements=None,
            last_edit=datetime.now().date(),
            user=User.objects.get(username=self.user_name_one),
        )


        # Create one booking for client_one
        start_date_one = datetime.now()
        end_date_one = start_date_one + timedelta(days=1)
        Booking.objects.create(
            start_date=start_date_one,
            end_date=end_date_one,
            product=productA,
            user=client_one,
            status=BookingStatus.objects.get(id=State.PENDING)
        )

    # Client 2 with three bookings
        self.client_two = Client.objects.create(  # Store as instance variable
            first_name="Jane",
            last_name="Smith",
            gender="F",
            street="456 Elm St",
            postcode="67890",
            city="Los Angeles",
            country="USA",
            phone="987-654-3210",
            email=self.user_name_two,
            unokod="DEF456",
            day_of_birth=datetime.now().date() + timedelta(weeks=-1500),
            personnr_lastnr="5678",
            region=region,
            requirements=None,
            last_edit=datetime.now().date(),
            user=User.objects.get(username=self.user_name_two),
        )

        # Create three bookings for client_two
        booking_dates = [
            (datetime.now() + timedelta(days=2), datetime.now() + timedelta(days=3)),
            (datetime.now() + timedelta(days=4), datetime.now() + timedelta(days=5)),
            (datetime.now() + timedelta(days=6), datetime.now() + timedelta(days=7)),
        ]

        for start, end in booking_dates:
            Booking.objects.create(
                start_date=start,
                end_date=end,
                product=productA,
                user=self.client_two,  
                status=BookingStatus.objects.get(id=State.PENDING)
            )


    def test_get_user_shelter_stay_count(self):
        start_date = datetime.now().date().isoformat()  
        end_date = (datetime.now().date() + timedelta(days=1)).isoformat() 
        
        url = f"/api/caseworker/guests/nights/count/1/{start_date}/{end_date}"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)

        self.assertIn("user_id", response_data)
        self.assertEqual(response_data["user_id"], 1)

        self.assertIn("user_stay_counts", response_data)
        self.assertIsInstance(response_data["user_stay_counts"], list)
        self.assertGreater(len(response_data["user_stay_counts"]), 0)

        first_stay = response_data["user_stay_counts"][0]
        self.assertIn("total_nights", first_stay)
        self.assertEqual(first_stay["total_nights"], 1)

        self.assertIn("start_date", first_stay)
        self.assertEqual(first_stay["start_date"], start_date)
        self.assertIn("end_date", first_stay)
        self.assertEqual(first_stay["end_date"], end_date)

        self.assertIn("host", first_stay)
        host = first_stay["host"]
        self.assertIn("id", host)
        self.assertEqual(host["id"], 1)
        self.assertIn("name", host)
        self.assertEqual(host["name"], "Host 1")
        self.assertIn("street", host)
        self.assertEqual(host["street"], "")
        self.assertIn("postcode", host)
        self.assertEqual(host["postcode"], "")
        self.assertIn("city", host)
        self.assertEqual(host["city"], "Malmö")

        self.assertIn("region", host)
        region = host["region"]
        self.assertIn("id", region)
        self.assertEqual(region["id"], 1)
        self.assertIn("name", region)
        self.assertEqual(region["name"], "Malmö")

    def test_get_user_shelter_stay_multiple_bookings(self):
        start_date = datetime.now().date().isoformat()  
        end_date = (datetime.now().date() + timedelta(days=30)).isoformat() 

        url = f"/api/caseworker/guests/nights/count/2/{start_date}/{end_date}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        print("Bookings for client two:", Booking.objects.filter(user=self.client_two).count())

        self.assertIn("user_id", response_data)
        self.assertEqual(response_data["user_id"], 2)
        self.assertGreaterEqual(len(response_data["user_stay_counts"]), 2) 


    def tearDown(self):
    # Delete all bookings created during tests
        Booking.objects.all().delete()
        
        # Delete all clients created during tests
        Client.objects.all().delete()
        
        # Delete all products created during tests
        Product.objects.all().delete()
        
        # Delete all hosts created during tests
        Host.objects.all().delete()
        
        # Delete all regions created during tests
        Region.objects.all().delete()
        
        # Delete all booking statuses created during tests
        BookingStatus.objects.all().delete()
        
        # Delete all users created during tests
        User.objects.all().delete()

