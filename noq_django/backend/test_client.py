from django.test import TestCase
from .models import Client, Region, User


class test_Client(TestCase):

    def setUp(self):
        region = Region(name="City")
        region.save()

    def test_region_get(self):
        region = Region.objects.get(name="City")
        self.assertIsInstance(region, Region)

    def test_user(TestCase):
        user = User()
        user.save()

        region = Region.objects.get(name="City")
        client = Client(
            first_name="Tom Sawyer",
            # user_type=man,
            gender="M",
            phone="123",
            email="a@e.se",
            unokod="UNO1234",
            region=region,
            user=user,
        )
        client.save()
