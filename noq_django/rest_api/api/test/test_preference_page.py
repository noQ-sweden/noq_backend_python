from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from backend.models import UserProfile, User
from rest_framework.test import APIClient

class UserProfileAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client.login(username='testuser', password='password123')

        self.user_profile = UserProfile.objects.create(
            user=self.user,
            uno="12345",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            sex="M",
            birthday="1990-01-01",
            language="en",
            presentation="Hello, I am John",
        )

    def test_create_profile(self):
        url = "/api/preferences/"
        data = {
            "uno": "54321",
            "first_name": "Jane",
            "last_name": "Smith",
            "sex": "F",
            "birthday": "1992-02-02",
            "email": "jane.smith@example.com",
            "telephone": "123456789",
            "language": "en",
            "presentation": "Hello, I am Jane",
            "supporting_person_id": None,
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["first_name"], "Jane")

    def test_get_profile(self):
        url = f"/api/preferences/{self.user.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "john.doe@example.com")

    def test_update_profile(self):
        url = f"/api/preferences/{self.user.id}/"

        data = {
            "first_name": "Jonathan",
            "last_name": "Doe",
            "email": "jonathan.doe@example.com",
            "language": "sv",
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Jonathan")

    def test_delete_profile(self):
        url = f"/api/preferences/{self.user.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["success"], True)

    def test_create_profile_with_existing_uno(self):
        url = "/api/preferences/"
        data = {
            "uno": "12345",  # Already used UNO
            "first_name": "Mark",
            "last_name": "Twain",
            "sex": "M",
            "birthday": "1985-06-15",
            "email": "mark.twain@example.com",
            "telephone": "987654321",
            "language": "en",
            "presentation": "Hello, I am Mark",
            "supporting_person_id": None,
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("UNO already exists", str(response.data))
