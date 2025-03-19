import json
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from django.core.cache import cache
from django.contrib.auth.models import User

class TestSSEBookingUpdates(TestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")

    @patch("backend.views.cache.get")  
    @patch("backend.views.cache.delete")  
    def test_sse_booking_updates(self, mock_cache_delete, mock_cache_get):
        """Test that the SSE stream sends booking updates."""

        # The test data to simulate
        test_booking_data = {"booking_id": 123, "status": "confirmed"}

        # Mock the cache.get to return test data once and then None
        mock_cache_get.return_value = test_booking_data  # Just return test data

        # Get the URL for the SSE view
        url = reverse('sse_booking_updates')  

        # Simulate making the request to the SSE endpoint
        response = self.client.get(url, **{"HTTP_ACCEPT": "text/event-stream"})

        # Check that the response is a StreamingHttpResponse
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/event-stream')

        # Read the response content, which should be an SSE message
        data_received = ""
        for chunk in response.streaming_content:
            data_received += chunk.decode()
            if data_received:  # Stop once we have received data
                break

        # Ensure the data received is valid JSON
        try:
            json_data_received = json.loads(data_received.split("data: ")[1].strip())
        except json.JSONDecodeError as e:
            self.fail(f"Failed to parse SSE data as JSON: {e}")

        # Check that the expected data was sent in the SSE stream
        self.assertEqual(json_data_received, test_booking_data)

        # Now exhaust the generator and check if cache.delete was called
        list(response.streaming_content)

        # Check if cache.delete was called with the expected key
        mock_cache_delete.assert_called_once_with(f"booking_update_{self.user.id}")

