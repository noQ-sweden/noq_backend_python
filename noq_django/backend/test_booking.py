import json
import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Booking
from .views import sse_booking_updates_view
from datetime import datetime


class SSEBookingUpdatesViewTest(TestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username="testuser", password="testpass")

    @patch('backend.views.booking_status_stream')
    def test_sse_booking_updates_view(self, mock_booking_status_stream):
        # Mock the generator returned by the booking_status_stream function
        mock_booking_status_stream.return_value = iter(["data: []\n\n"])

        # simulate a GET request to the view
        client = Client()
        client.login(username="testuser", password="testpass")
        response = client.get('/sse/booking_updates/')

        # Check the response content type and headers
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/event-stream')
        self.assertEqual(response['Cache-Control'], 'no-cache')
        self.assertEqual(response['Connection'], 'keep-alive')

        # Check that the mock booking stream was called
        mock_booking_status_stream.assert_called_once_with(self.user.id)

        # Since the response is streaming, access streaming_content instead of content
        response_data = ''.join([chunk.decode() for chunk in response.streaming_content])
        self.assertIn("data: []\n\n", response_data)

    @patch('backend.views.booking_status_stream')
    def test_sse_booking_updates_view_no_loggedin_user(self, mock_booking_status_stream):
        # Test for a user who is not logged in
        client = Client()
        response = client.get('/sse/booking_updates/')

        # if not loggedin, gets redirected to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
