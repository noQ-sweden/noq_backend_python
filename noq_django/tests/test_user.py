from django.test import TestCase
from backend.models import Client


class old_tst__UserTestClass(TestCase):
    def setUp(self):
        Client.objects.create(first_name="Tom", gender="M")
        # Reservation.objects.create(name="lion", sound="roar")

    def old_tst_animals_can_speak(self):
        tom = Client.objects.get(first_name="Tom")

        self.assertIsNotNone(tom)