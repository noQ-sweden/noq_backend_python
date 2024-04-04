from django.test import TestCase
from backend.models import Client, Reservation


def test_first():
    assert 2 is not None


class test_UserTestClass(TestCase):
    def setUp(self):
        Client.objects.create(name="Tom")
        # Reservation.objects.create(name="lion", sound="roar")

    def test_animals_can_speak(self):
        tom = Client.objects.get(name="Tom")

        self.assertIsNotNone(tom)
