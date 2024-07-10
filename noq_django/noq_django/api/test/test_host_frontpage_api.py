import sys
sys.path.append("....backend") # Adds folder where backend is to python modules path.
import json
from datetime import datetime, timedelta
from django.test import TestCase
from django.contrib.auth.models import User, Group
from backend.models import Host, Client, Product, Region, Booking, State, BookingStatus
from .test_data import TestData

class TestHostFrontpageApi(TestCase):
    t_data = None


    def setUp(self):
        self.t_data = TestData()
        # 1st user will be in group "host" and rest will be in group "user"
        self.t_data.user_login(user_group="host", nr_of_users=5)


    def connect_user_and_host(self, host_number):
        # Connect host_user and host
        host = self.t_data.hosts[host_number]
        # Host user is always first in the array
        host_user = self.t_data.users[0]
        host.users.add(host_user)
        host.save()


    def test_get_host_info(self):
        self.connect_user_and_host(host_number=0)
        host = self.t_data.hosts[0]

        response = self.t_data.test_client.get("/api/host/")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['name'], host.name)


    def test_get_host_info_no_host(self):
        response = self.t_data.test_client.get("/api/host/")

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(data['detail'], "User is not admin to a host.")


    def test_get_available_places_host(self):
        self.connect_user_and_host(host_number=1)
        host = self.t_data.hosts[1]

        # Get products that will be booked, Host 2 has two products
        # Product 1 has 6 places, product 2 has 8 places
        products = Product.objects.filter(host_id=host).all()
        clients = Client.objects.all()

        current_date = datetime.now().date()
        # Add bookings for the client_user (brukare)
        for i in range(6):
            # 5 bookings for today, 1 for tomorrow
            extra_day = 1 if i > 3 else 0
            # Bookings:
            # Product 1: today: 3
            # Product 2: today: 1, tomorrow: 2
            product_idx = 1 if i > 2 else 0
            Booking.objects.create(
                start_date=current_date + timedelta(days=extra_day),
                end_date=current_date + timedelta(days=extra_day+1),
                product=products[product_idx],
                user=clients[i % 4],
                status=BookingStatus.objects.create(description="reserved"),
            )
        bookings = Booking.objects.all()
        # Get availability for two days
        response = self.t_data.test_client.get("/api/host/available/2")

        self.assertEqual(response.status_code, 200)

        tomorrows_date = current_date + timedelta(days=1)
        data = json.loads(response.content)
        # 3 places booked from 1st product for today, 1 booked for 2md product
        self.assertEqual(data['available_dates'][str(current_date)][0]['places_left'], 6 - 3)
        self.assertEqual(data['available_dates'][str(current_date)][1]['places_left'], 8 - 1)
        # 1 place booked from 1st product
        self.assertEqual(data['available_dates'][str(tomorrows_date)][0]['places_left'], 6)
        self.assertEqual(data['available_dates'][str(tomorrows_date)][1]['places_left'], 6)


    def tearDown(self):
        # After the tests delete all data generated for the tests
        self.t_data.delete_products()
        self.t_data.delete_users()
