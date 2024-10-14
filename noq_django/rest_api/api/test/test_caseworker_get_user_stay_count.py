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

    caseworker_user = None
    caseworker_name = "user.caseworker@test.nu"
    user_name_one = "user.user1@test.nu"
    user_name_two = "user.user2@test.nu"
    user_name_three = "user.user3@test.nu"
    password = "VeryBadPassword!"

    def create_user(self, username, group):
        user = User.objects.create_user(username=username, password=self.password)
        group_obj, created = Group.objects.get_or_create(name=group)
        user.groups.add(group_obj)

    def caseworker_login(self):
        # Create host user and client users for the test
        if User.objects.filter(username=self.caseworker_name).first() == None:
            client_user_one = self.create_user(self.user_name_one, "user")
            client_user_two = self.create_user(self.user_name_two, "user")
            client_user_three = self.create_user(self.user_name_three, "user")
            caseworker_user = self.create_user(self.caseworker_name, "caseworker")

       # Skriv ut alla användare som finns just nu
        print("Users after creating clients:")
        for user in User.objects.all():
            print(f"Username: {user.username}, ID: {user.id}")

        # Login the caseworker
        self.client = TestClient(router)
        self.client.login(username=self.caseworker_name, password=self.password)
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
        self.caseworker_login()

        # Create products that can be used during the tests
        if Product.objects.filter(id=1).first() is None:
            region = Region.objects.create(name="Malmö")
            hostA = Host.objects.create(name="Host 1", street="", postcode="", city="Malmö", region_id=region.id)
            productA = Product.objects.create(name="room", total_places=5, host_id=hostA.id, type="room")

        user_group = Group.objects.get(name="user")

        # Create clients
        clients = []
        for i, user in enumerate(User.objects.filter(groups=user_group), start=1):
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
                user=user,
            )
            clients.append(client)

        # Create statuses
        statuses = [
            {"id": State.PENDING, "description": "pending"},
            {"id": State.DECLINED, "description": "declined"},
            {"id": State.ACCEPTED, "description": "accepted"},
            {"id": State.CHECKED_IN, "description": "checked_in"},
            {"id": State.IN_QUEUE, "description": "in_queue"},
            {"id": State.RESERVED, "description": "reserved"},
            {"id": State.CONFIRMED, "description": "confirmed"},
            {"id": State.ADVISED_AGAINST, "description": "advised_against"},
        ]

        for status in statuses:
            if not BookingStatus.objects.filter(id=status["id"]).exists():
                booking_status = BookingStatus.objects.create(
                    id=status["id"], description=status["description"]
                )
                booking_status.save()

        # Create bookings based on requirements
        host = Host.objects.get(name="Host 1")
        host_products = Product.objects.filter(host=host)

        client_one = Client.objects.get(user=User.objects.get(username=self.user_name_one))
        booking_1 = Booking(
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=1),
            product=host_products.first(),
            user=client_one,
            status=BookingStatus.objects.get(id=State.PENDING)
        )
        booking_1.save()

        client_two = Client.objects.get(user=User.objects.get(username=self.user_name_two))
        booking_dates = [
            (datetime.now(), datetime.now() + timedelta(days=1)),  
            (datetime.now() + timedelta(days=1), datetime.now() + timedelta(days=2)),  
            (datetime.now() + timedelta(days=2), datetime.now() + timedelta(days=4)),  
        ]

        for start, end in booking_dates:
            booking = Booking(
                start_date=start,
                end_date=end,
                product=host_products.first(),
                user=client_two,
                status=BookingStatus.objects.get(id=State.PENDING)
            )
            booking.save()


    def test_client_multiple_stays(self):

        user_two = User.objects.filter(username=self.user_name_two).first()

        start_date = datetime.now().date().isoformat()  
        end_date = (datetime.now().date() + timedelta(days=30)).isoformat() 
        url = f"/api/caseworker/guests/nights/count/{user_two.id}/{start_date}/{end_date}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)

        self.assertEqual(response_data["user_id"], user_two.id)
        
        self.assertGreaterEqual(len(response_data["user_stay_counts"]), 3)  
    
    """
    def test_client_with_one_stay(self):
        
        user_one = User.objects.filter(username=self.user_name_one).first()
        print("USER ONE",user_one.__dict__)

        client_one = Client.objects.filter(user=user_one).first()
        print("CLIENT ONE:", client_one.__dict__)
        user_one_bookings = Booking.objects.filter(user=client_one)

        # Skriver ut alla bokningar för user_one
        for booking in user_one_bookings:
            print("BOOKING", booking.__dict__)

        start_date = datetime.now().date().isoformat()  
        end_date = (datetime.now().date() + timedelta(days=30)).isoformat() 

        url = f"/api/caseworker/guests/nights/count/{user_one.id}/{start_date}/{end_date}"

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        print("DATA", response_data)

        self.assertEqual(response_data["user_id"], user_one.id)

        self.assertEqual(len(response_data["user_stay_counts"]), 1)  
    """
    def test_client_no_stays(self):

        user_three = User.objects.filter(username=self.user_name_three).first()

        start_date = datetime.now().date().isoformat()  
        end_date = (datetime.now().date() + timedelta(days=30)).isoformat() 

        url = f"/api/caseworker/guests/nights/count/{user_three.id}/{start_date}/{end_date}"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        
        self.assertEqual(response_data['user_stay_counts'], [])


    def tearDown(self):
        User.objects.all().delete()
        Client.objects.all().delete()
        Booking.objects.all().delete()
        Product.objects.all().delete()

