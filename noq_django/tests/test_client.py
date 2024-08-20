from django.test import TestCase
from backend.models import Client, Region, User

class TestClient(TestCase):

    def setUp(self):
        self.region = Region.objects.create(name="City")

    def test_region_get(self):
        region = Region.objects.get(name="City")
        self.assertIsInstance(region, Region)

    def test_user_creation(self):
        user = User.objects.create(username="testuser")

        region = Region.objects.get(name="City")

        client = Client(
            first_name="Tom",
            last_name="Sawyer",
            gender="M",
            phone="123",
            email="a@e.se",
            unokod="UNO1234",
            region=region,
            user=user,
        )
        client.save()

        self.assertTrue(Client.objects.filter(email="a@e.se").exists())
