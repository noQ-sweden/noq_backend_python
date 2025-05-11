import sys
sys.path.append("....backend")
import json
from django.test import TestCase
from django.contrib.auth.models import User, Group
from backend.models import (Host, Client, Product, Region, Booking,
                            Available, State, BookingStatus)
from datetime import datetime, timedelta
from .test_data import TestData
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core import mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator

class TestUserRegistrationApi(TestCase):
    def setUp(self):
        self.region = Region.objects.create(name="Test Region")
        Group.objects.get_or_create(name="user")

    def test_registration_user(self):
        # Prepare test data
        data = {
            "email": "testuser1234123@example.com",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        url = "/api/register/"

        # Send POST request with headers
        response = self.client.post(
            url,
            data,
            content_type="application/json",
            **{"HTTP_X-User-Role": "user"}
        )

        # Check response status
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(
            body["success"],
            "Användare registrerad! – kolla mejlen för aktivering"
        )
        user_id = body["user_id"]

        # Check that the User was created
        self.assertTrue(User.objects.filter(email=data["email"]).exists())
        user = User.objects.get(email=data["email"])

        # Verify the user belongs to the "user" group
        self.assertTrue(user.groups.filter(name="user").exists())

        # Check that the Client record was created
        self.assertTrue(Client.objects.filter(email=data["email"]).exists())

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, [data["email"]])
        self.assertIn("Välkommen till NoQ – aktivera ditt konto", email.subject)

        uidb64 = urlsafe_base64_encode(force_bytes(user_id))
        self.assertIn(f"{settings.FRONTEND_URL}{uidb64}/", email.body)

        user = User.objects.get(pk=user_id)
        self.assertFalse(user.is_active)
        self.assertTrue(Client.objects.filter(user=user).exists())

#test the email link activation api
class TestUserActivationApi(TestCase):
    def setUp(self):
        # Create one inactive user
        self.user = User.objects.create_user(
            email="activate_me@example.com",
            username="activate_me@example.com",
            password="SomePass!23",
            first_name="Activate",
            last_name="Me",
            is_active=False,
        )
        # Pre‐compute uidb64 and token for all tests
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)
        self.url = f"/api/activate/{self.uidb64}/{self.token}/"

    def test_activate_user_success(self):
        # First POST should activate the user
        response = self.client.post(self.url, content_type="application/json")
        self.assertEqual(response.status_code, 200)

        body = response.json()
        self.assertEqual(body.get("message"), "Konto aktiverat.")

        # Reload from DB and check is_active
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_activate_token_reuse_fails(self):
        # First activation
        self.client.post(self.url, content_type="application/json")
        # Second activation attempt should fail
        response2 = self.client.post(self.url, content_type="application/json")
        self.assertEqual(response2.status_code, 400)

        body2 = response2.json()
        self.assertEqual(
            body2.get("error"),
            "Länken är ogiltig eller har gått ut."
        )
        # User remains active (since first call worked)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_activate_with_invalid_token(self):
        # Use a wrong token
        bad_url = f"/api/activate/{self.uidb64}/not-a-valid-token/"
        response = self.client.post(bad_url, content_type="application/json")
        self.assertEqual(response.status_code, 400)

        body = response.json()
        self.assertEqual(
            body.get("error"),
            "Länken är ogiltig eller har gått ut."
        )
        # User still inactive
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_activate_with_bad_uid(self):
        # Malformed uidb64
        bad_url = f"/api/activate/bad-uidb64/{self.token}/"
        response = self.client.post(bad_url, content_type="application/json")
        self.assertEqual(response.status_code, 400)

        body = response.json()
        self.assertEqual(
            body.get("error"),
            "Ogiltig aktiveringslänk."
        )
        # User still inactive
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

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
        # log in user for the tests
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
        end_date = start_date + timedelta(days=1)
        host_id = Product.objects.get(total_places=4).host.id

        data = {
            "start_date": start_date,
            "end_date": end_date,
            "host_id": host_id
        }

        url = "/api/user/request_booking"
        response = self.t_data.test_client.post(url, data, content_type='application/json')

        # Check status code is 200 and the status of the booking is pending
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["status"]["description"], "pending")


    def test_book_a_product_full(self):
        '''
        Step 0: Remove all products except one
        Step 1: Create one booking for product with one places
        Step 2: Create second overlapping booking and get back
                a list of available places per day

        Dates    1
        Booking1 |
        Booking2 |
        Expected 1

        Booking2 is not accepted and API returns list of bookings count
        per day and the max amount of places. End date is not included
        in the list.
        '''

        # Step 0: Remove all products except one
        Product.objects.filter(total_places__gt=1).delete()
        self.assertEqual(Product.objects.all().count(), 1)


        # Step 1: Create a booking for user 2
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=1)
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

        # Step 2: Create second booking for same dates that doesn't pass the validation
        # as there is no free rooms available
        host_id = Product.objects.get(total_places=1).host.id

        data = {
            "start_date": start_date,
            "end_date": end_date,
            "host_id": host_id
        }

        url = "/api/user/request_booking"
        response = self.t_data.test_client.post(url, data, content_type='application/json')

        # Check status code is 200 and the bookings count matches
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.content)
        self.assertEqual(data['detail'], "No available product found for the selected date.")

    def test_delete_reserved_booking(self):
        # Step 1: Create a booking for the test user
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=1)
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


    def test_get_available_products_with_dates(self):
        """
        Ensure the API returns all available products for a given host along with their available dates.
        """
        today = datetime.now().date()

        # Step 1: Create a host
        region = Region.objects.create(name="Test Region")
        host = Host.objects.create(name="Test Host", region=region, street="Test Street", city="Test City")

        # Step 2: Create products linked to this host
        product1 = Product.objects.create(name="Room A", description="Single room", total_places=2, host=host, type="room")
        product2 = Product.objects.create(name="Room B", description="Double room", total_places=4, host=host, type="room")

        # Step 3: Create available entries (dates when products are available)
        Available.objects.create(product=product1, available_date=today)
        future_date1 = today + timedelta(days=1)
        future_date2 = today + timedelta(days=2)
        Available.objects.create(product=product1, available_date=future_date1)
        Available.objects.create(product=product2, available_date=future_date2)

        # Step 4: Make a GET request to fetch available products for the host
        url = f"/api/user/available_host/{host.id}"
        response = self.t_data.test_client.get(url)

        # Step 5: Verify response status
        self.assertEqual(response.status_code, 200)

        # Step 6: Parse response JSON
        data = json.loads(response.content)

        # Step 7: Verify host details
        self.assertEqual(data[0]["host"]["id"], host.id)
        self.assertEqual(data[0]["host"]["name"], host.name)

        # Step 8: Verify the products and their availability dates
        self.assertEqual(len(data[0]["products"]), 2)  # Ensure 2 products are returned

        products = {p["id"]: p for p in data[0]["products"]}
        #ensure expected product data
        expected_products = {
            product1.id: {
                "name": "Room A",
                "places_left": 1,
                "available_dates": [
                    {"available_date": str(today)},
                    {"available_date": str(future_date1)},
                ],
            },
            product2.id: {
                "name": "Room B",
                "places_left": 0,
                "available_dates": [
                    {"available_date": str(future_date2)},
                ],
            },
        }

        # Loop through and assert each product
        for product_id, expected in expected_products.items():
            product_data = products[product_id]
            self.assertEqual(product_data["name"], expected["name"])
            self.assertEqual(product_data["places_left"], expected["places_left"])
            self.assertCountEqual(product_data["available_dates"], expected["available_dates"])


    def test_book_a_product_wrong_gender(self):
        '''
        NOTE! Keep this test case as last in the file, as it logs in as a male user

        Step 0: Remove all products except one women-only product
        Step 1: Log in as a male user
        Step 2: Try to book women only product

        Booking is not accepted and API returns 409 with correct info.
        '''

        # Step 0: Remove all products except one
        Product.objects.filter(total_places__gt=1).delete()
        self.assertEqual(Product.objects.all().count(), 1)

        # Step 1: Log in as a male user
        # Create new user
        username = "maleuser"
        password = "badpassword"
        user = User.objects.create_user(username=username, password=password)
        group_obj, created = Group.objects.get_or_create(name="user")
        user.groups.add(group_obj)
        client = Client.objects.create(
            first_name=username,
            gender="M",
            user=user,
            region=self.t_data.region)

        # Login the first user
        self.t_data.test_client.login(username=username, password=password)

        # Step 2: Try to book women only product
        # Set product as women-only
        product = Product.objects.get(total_places=1)
        product.type = "woman_only"
        product.save()

        start_date = datetime.now().date() + timedelta(days=1)
        end_date = start_date + timedelta(days=1)

        data = {
            "start_date": start_date,
            "end_date": end_date,
            "host_id": product.host.id
        }

        url = "/api/user/request_booking"
        response = self.t_data.test_client.post(url, data, content_type='application/json')

        # Check status code is 409 and the message is correct
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.content)
        self.assertEqual(data['detail'], "User can't book woman only product.")


    def tearDown(self):
        # After the tests delete all data generated for the tests
        self.t_data.delete_users()
        self.t_data.delete_products()
