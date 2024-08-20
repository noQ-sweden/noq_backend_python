from django.test import TestCase
from backend.models import Client

class UserTestClass(TestCase):
    def setUp(self):
        self.client = Client.objects.create(first_name="Tom", gender="M")
        # Reservation.objects.create(name="lion", sound="roar")

    def test_client_creation(self):
        tom = Client.objects.get(first_name="Tom")
        self.assertIsNotNone(tom)

    def test_client_gender(self):
        tom = Client.objects.get(first_name="Tom")
        self.assertEqual(tom.gender, "M")

    def test_client_update(self):
        tom = Client.objects.get(first_name="Tom")
        tom.first_name = "Jerry"
        tom.save()
        updated_tom = Client.objects.get(pk=tom.pk)
        self.assertEqual(updated_tom.first_name, "Jerry")

    def test_client_deletion(self):
        tom = Client.objects.get(first_name="Tom")
        tom.delete()
        with self.assertRaises(Client.DoesNotExist):
            Client.objects.get(first_name="Tom")

    def test_client_list(self):
        Client.objects.create(first_name="Jerry", gender="M")
        clients = Client.objects.all()
        self.assertEqual(clients.count(), 2)