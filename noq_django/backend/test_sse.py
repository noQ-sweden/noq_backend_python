from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from backend.models import Booking, BookingStatus, Client as ClientModel, Region, Product, Host, ProductRequirement
import json
import time
from django.utils import timezone
from datetime import timedelta

class SSEBookingStatusTestCase(TestCase):

    def test_sse_booking_status_updates(self):
        """Test that SSE endpoint streams booking updates."""

        # Define the future start date 
        future_start_date = timezone.now() + timedelta(days=1)

        # Try to get the product by ID, and create it if it doesn't exist
        try:
            product = Product.objects.get(id=1)
        except Product.DoesNotExist:
            # Create the Region, Host, and Product if they don't exist
            region = Region.objects.create(name='Default Region')  # Create a default region
            host = Host.objects.create(name="Test Host", region=region)  # Create a test host linked to the region
            product = Product.objects.create(
                name="Test Product",
                description="Test description",
                total_places=10,
                host=host,
                type='room',  
                room_location='Sovsal',  
                bookable=True
            )

        # Create a User (for authentication)
        user = User.objects.create_user(
            username="john_doe",
            email="john@example.com",
            password="testpassword123"
        )

        # Create a Region
        region = Region.objects.create(name='Some Region')

        # Create a Client (linked to User)
        client_user = ClientModel.objects.create(
            user=user,
            first_name="John",
            last_name="Doe",
            phone="+1234567890",
            email="john@example.com",
            gender="Male",
            region=region,
           
        )

        # Create booking statuses
        status_pending = BookingStatus.objects.create(description="Pending")

        # Create a test booking linked to the Client
        booking = Booking.objects.create(
            user=client_user,
            status=status_pending,
            start_date=future_start_date,
            end_date=future_start_date + timedelta(days=5),
            product=product  
        )

        # Authenticate the user
        client = Client()
        client.login(username="john_doe", password="testpassword123")

        # Hit the SSE endpoint
        url = reverse('sse_booking_updates') 
        response = client.get(url, stream=True)

        # Ensure the connection is established
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/event-stream')

        # Read the first chunk of data from the stream
        first_chunk = next(response.streaming_content)
        decoded_data = first_chunk.decode('utf-8').strip()

        # Check if the response contains valid SSE data
        self.assertTrue(decoded_data.startswith("data: "))

        # Extract the JSON part from the SSE event
        data_part = decoded_data.replace("data: ", "").strip()
        booking_data = json.loads(data_part)

        # Verify the booking content matches the database
        self.assertEqual(booking_data['status'], 'Pending')
        self.assertEqual(booking_data['user'], 'John Doe')
        self.assertEqual(booking_data['start_date'], future_start_date.strftime('%Y-%m-%d'))  

    def test_booking_status_change_triggers_sse_update(self):
        """Test that when the booking status changes, the SSE updates."""

        # Define the future start date
        future_start_date = timezone.now() + timedelta(days=1)

        # Try to get the product by ID, and create it if it doesn't exist
        try:
            product = Product.objects.get(id=1)
        except Product.DoesNotExist:
            # Create the Region, Host, and Product if they don't exist
            region = Region.objects.create(name='Default Region')  
            host = Host.objects.create(name="Test Host", region=region)  
            product = Product.objects.create(
                name="Test Product",
                description="Test description",
                total_places=10,
                host=host,
                type='room', 
                room_location='Sovsal', 
                bookable=True
            )

        # Create a User and Client (same as in the previous test)
        user = User.objects.create_user(
            username="john_doe",
            email="john@example.com",
            password="testpassword123"
        )

        # Create the client
        client_user = ClientModel.objects.create(
            user=user,
            first_name="John",
            last_name="Doe",
            phone="+1234567890",
            email="john@example.com",
            gender="Male",
            region=region
        )

        # Create booking statuses
        status_pending = BookingStatus.objects.create(description="Pending")
        status_confirmed = BookingStatus.objects.create(description="Confirmed")

        # Create the booking
        booking = Booking.objects.create(
            user=client_user,
            status=status_pending,
            start_date=future_start_date,
            end_date=future_start_date + timedelta(days=5),
            product=product  
        )




        # Authenticate the user
        client = Client()
        client.login(username="john_doe", password="testpassword123")

        # Hit the SSE endpoint
        url = reverse('sse_booking_updates')  
        response = client.get(url, stream=True)

        # Change the booking status after 2 seconds
        time.sleep(2)
        booking.status = status_confirmed
        booking.save()

        # Read the next chunk from the stream
        next_chunk = next(response.streaming_content).decode('utf-8').strip()
        data_part = next_chunk.replace("data: ", "").strip()
        updated_data = json.loads(data_part)

        # Verify the booking status has changed
        self.assertEqual(updated_data['status'], 'Confirmed')
        self.assertEqual(updated_data['user'], 'John Doe')

    def test_unauthorized_user_cannot_access_sse(self):
        """Test that an unauthorized user cannot access the SSE."""

        # Logout the user
        client = Client()
        client.logout()

        # Attempt to connect to SSE
        url = reverse('sse_booking_updates')  
        response = client.get(url)

        # It should block the request with a 302 redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

