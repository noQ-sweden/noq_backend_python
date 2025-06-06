import sys
sys.path.append("....backend") 
import json
from datetime import datetime, timedelta
from django.test import TestCase
from django.core import mail
from django.contrib.auth.models import User, Group
from backend.models import (
    Host, Client, Product, Region, Booking, BookingStatus, Available
)
from django.test import Client as TestClient
from ..volunteer_api import router  
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core import mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator


class TestVolunteerRegistrationApi(TestCase):
    def setUp(self):
        self.region = Region.objects.create(name="Test Region")
        Group.objects.get_or_create(name="volunteer")

    def test_registration_volunteer(self):
        # Prepare test data
        data = {
            "email": "volunteertestuser1234@example.com",
            "password": "SecurePass123!",
            "first_name": "volunteer",
            "last_name": "User"
        }
        url = "/api/register/"

        # Send POST request with headers
        response = self.client.post(
            url,
            data,
            content_type="application/json",
            **{"HTTP_X-User-Role": "volunteer"}
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

        # Verify the user belongs to the "volunteer" group
        self.assertTrue(user.groups.filter(name="volunteer").exists())

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

class TestVolunteerApi(TestCase):
    # Constants for test data
    VOLUNTEER_USERNAME = "volunteer@test.com"
    PASSWORD = "TestPassword123!"
    CLIENT_EMAIL = "guest@test.com"

    def setUp(self):
        # Create a volunteer user and set up initial data
        self.volunteer_user = User.objects.create_user(
            username=self.VOLUNTEER_USERNAME, password=self.PASSWORD
        )
        volunteer_group, _ = Group.objects.get_or_create(name="volunteer")
        self.volunteer_user.groups.add(volunteer_group)

        # Set up test client for making requests
        self.client = TestClient(router)
        self.client.login(username=self.VOLUNTEER_USERNAME, password=self.PASSWORD)

        # Create a region, host, product, and client data
        self.region = Region.objects.create(name="Stockholm")
        self.host = Host.objects.create(name="TestHost", city="Stockholm", region=self.region)
        self.product = Product.objects.create(name="TestRoom", total_places=5, host=self.host, type="room")
        self.client_user = Client.objects.create(
            first_name="Guest",
            last_name="User",
            email=self.CLIENT_EMAIL,
            region=self.region,
            user=self.volunteer_user,
            gender="M"  # Add gender here (e.g., "M" or "K")
    )

    def test_request_booking(self):
        # Define booking dates
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=2)

        # Prepare booking data
        booking_data = {
            "product_id": self.product.id,
            "user_id": self.client_user.id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }

        # Send POST request to create booking
        response = self.client.post("/api/volunteer/booking/request", json.dumps(booking_data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        
        booking = Booking.objects.get(id=response.json().get("id"))
        self.assertEqual(booking.user.id, self.client_user.id)
        self.assertEqual(booking.status.description, "pending")

    def test_confirm_booking(self):
        # Create a pending booking for confirmation
        booking = Booking.objects.create(
            start_date=datetime.now().date(),
            end_date=datetime.now().date() + timedelta(days=2),
            product=self.product,
            user=self.client_user,
            status=BookingStatus.objects.get(description="pending")
        )

        # Confirm the booking
        response = self.client.patch(f"/api/volunteer/booking/confirm/{booking.id}")
        self.assertEqual(response.status_code, 200)

        booking.refresh_from_db()
        self.assertEqual(booking.status.description, "confirmed")

    """
    # Mail functionality is not in 
    def test_confirmation_email_sent(self):
        # Create a booking to confirm
        booking = Booking.objects.create(
            start_date=datetime.now().date(),
            end_date=datetime.now().date() + timedelta(days=2),
            product=self.product,
            user=self.client_user,
            status=BookingStatus.objects.get(description="pending")
        )

        # Confirm the booking and trigger email
        self.client.patch(f"/api/volunteer/booking/confirm/{booking.id}")

        # Verify email sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.CLIENT_EMAIL])
        self.assertIn("Booking Confirmation", mail.outbox[0].subject)
    """

    def tearDown(self):
        # Clean up all test data after each test
        Booking.objects.all().delete()
        Product.objects.all().delete()
        Client.objects.all().delete()
        Host.objects.all().delete()
        Region.objects.all().delete()
        User.objects.all().delete()
