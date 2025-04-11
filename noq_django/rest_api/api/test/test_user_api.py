
import sys
sys.path.append("....backend")
import json
from django.test import TestCase
from django.contrib.auth.models import User, Group
from backend.models import (Host, Client, Product, Region, Booking,
                            Available, State, BookingStatus)
from datetime import datetime, timedelta
from unittest.mock import patch
from django.urls import reverse
from .test_data import TestData

from django.core.cache import cache





# New Test Class for Login functionality
class TestUserApi(TestCase):
    def setUp(self):
        # Create a user for login testing
        self.test_user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            first_name="Test",
            last_name="User"
        )
        self.client = self.client_class()

    def test_user_login(self):
        # Simulate a login request
        url = "/api/login/"
        data = {
            "email": "testuser",
            "password": "testpassword"
        }
        response = self.client.post(url, data, content_type="application/json")
        
        # Check the response code is 200 (successful login)
        self.assertEqual(response.status_code, 200)
        
        # Parse the response content
        data = json.loads(response.content)

        # Parse the response for debbugin purposes
        print("Login response data:", data)
        
        # Check if the login was successful
        self.assertEqual(data["login_status"], True)
        
        # Verify that the correct first and last name are returned
        self.assertEqual(data["first_name"], "Test")
        self.assertEqual(data["last_name"], "User")

    def tearDown(self):
        # Cleanup the created user
        self.test_user.delete()

# Existing Test Class for Product API
class TestProductsApi(TestCase):
    t_data = None

    def setUp(self):
        # Add data to the db
        self.t_data = TestData()
        # log in host user for the tests
        self.t_data.user_login(user_group="user", nr_of_users=2)

class TestProductsApi(TestCase):
    t_data = None

    def setUp(self):
        # Add data to the db
        self.t_data = TestData()
        # log in host user for the tests
        self.t_data.user_login(user_group="user", nr_of_users=2)


    def test_get_available_products(self):
        # No Bookings, so expects to get five products (3 Host A, 2 Host B)
        current_date = datetime.now().date()
        url = "/api/user/available/" + str(current_date)
        response = self.t_data.test_client.get(url)

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
        response = self.t_data.test_client.post(url, data, content_type='application/json')

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
            user=User.objects.get(username=self.t_data.usernames[1]))

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
        response = self.t_data.test_client.post(url, data, content_type='application/json')

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

    def test_delete_reserved_booking(self):
        # Step 1: Create a booking for the test user
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=3)
        product = Product.objects.get(total_places=1)
        # Since only the first user is logged in the list of the two users, the booking will belong to the first user
        client = Client.objects.get(
            user=User.objects.get(username=self.t_data.usernames[0])) 

        booking = Booking(
            start_date=start_date,
            end_date=end_date,
            product=product,
            user=client,
            status=BookingStatus.objects.get(id=State.RESERVED)
        )
        booking.save()
        
        # Step 2: Perform DELETE request on the booking
        url = f"/api/user/bookings/{booking.id}"
        response = self.t_data.test_client.delete(url)

        # Step 3: Verify the response
        self.assertEqual(response.status_code, 200)

        # Step 4: Confirm the booking no longer exists in the database
        with self.assertRaises(Booking.DoesNotExist):
            Booking.objects.get(id=booking.id)


    def tearDown(self):
        # After the tests delete all data generated for the tests
        self.t_data.delete_users()
        self.t_data.delete_products()

 

class TestSSEApi(TestCase):
    def setUp(self):
        # Set up test data
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username='testuser', password='password')

        # Create region and client
        region = Region.objects.first() or Region.objects.create(name="Test Region")
        self.test_user = User.objects.create_user(username="clientuser", password="testpassword")
        client = Client.objects.create(user=self.test_user, gender='K', region=region)

        # Create a product with 1 available spot
        self.product = Product.objects.create(name="Test Product", total_places=1)

        # Create booking
        self.booking = Booking.objects.create(
            start_date=datetime.now().date(),
            end_date=datetime.now().date() + timedelta(days=1),
            product=self.product,
            user=client,
            status=BookingStatus.objects.get(id=State.PENDING)
        )

    def test_sse_booking_updates(self):
        """ Test that SSE streams live booking updates when the status changes. """

        user_id = self.user.id
        url = reverse('sse_booking_updates', kwargs={'user_id': user_id})
        response = self.client.get(url, **{"HTTP_ACCEPT": "text/event-stream"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/event-stream')

        # Trigger status change (which should invoke signal to update cache)
        new_status = BookingStatus.objects.get(id=State.CONFIRMED)
        self.booking.status = new_status
        self.booking.save()

        # Wait for signal to update the cache
        cache_key = f"booking_update_{self.booking.id}"
        cached_data = None
        for _ in range(10):
            cached_data = cache.get(cache_key)
            if cached_data:
                break

        self.assertIsNotNone(cached_data, "Cache was not updated by signal.")
        self.assertEqual(cached_data["status"], "confirmed")

        # Simulate receiving from the SSE stream
        data_received = ""
        for chunk in response.streaming_content:
            data_received += chunk.decode()
            if "data: " in data_received:
                break

        try:
            json_data_received = json.loads(data_received.split("data: ")[1].strip())
        except json.JSONDecodeError as e:
            self.fail(f"Failed to parse SSE data as JSON: {e}")

        self.assertEqual(json_data_received, cached_data)
