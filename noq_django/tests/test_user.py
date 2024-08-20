from django.test import TestCase
from backend.models import Client

class UserTestClass(TestCase):
    def setUp(self):
        Client.objects.create(first_name="Tom", gender="M")
        # Reservation.objects.create(name="lion", sound="roar")

    def test_client_creation(self):
        tom = Client.objects.get(first_name="Tom")
        self.assertIsNotNone(tom)