from django.test import TestCase
from backend.models import Client, Region, User

class TestClient(TestCase):

    def setUp(self):
        """Set up the test environment."""
        self.region = Region.objects.create(name="City")
        self.user = User.objects.create(username="testuser")

    def test_region_creation(self):
        """Test that a region can be created and retrieved."""
        region = Region.objects.get(name="City")
        self.assertIsInstance(region, Region)
        self.assertEqual(region.name, "City")

    def test_client_creation(self):
        """Test that a client can be created and associated with a region and user."""
        client = Client.objects.create(
            first_name="Tom",
            last_name="Sawyer",
            gender="M",
            phone="123",
            email="a@e.se",
            unokod="UNO1234",
            region=self.region,
            user=self.user,
        )
        self.assertTrue(Client.objects.filter(email="a@e.se").exists())
        self.assertEqual(client.first_name, "Tom")
        self.assertEqual(client.last_name, "Sawyer")
        self.assertEqual(client.gender, "M")
        self.assertEqual(client.phone, "123")
        self.assertEqual(client.email, "a@e.se")
        self.assertEqual(client.unokod, "UNO1234")
        self.assertEqual(client.region, self.region)
        self.assertEqual(client.user, self.user)