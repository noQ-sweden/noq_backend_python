import json
from django.test import TestCase
from backend.models import UserProfile, User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token  # Optional if using token auth

class UserProfileAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client.force_authenticate(user=self.user)  # Works for request.user in Django Ninja

        self.user_profile = UserProfile.objects.create(
            user=self.user,
            uno="12345",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            sex="M",
            birthday="1990-01-01",
            birth_year=1990,
            language="en",
            presentation="Hello, I am John",
        )

    def test_create_profile(self):
        user = User.objects.create_user(username="Test", password="Test1234")
        self.client.force_login(user)  # This sets request.user

        url = "/api/preferences/"
        data = {
            "uno": "54321",
            "first_name": "Jane",
            "last_name": "Test",
            "sex": "F",
            "birthday": "1992-02-02",
            "birth_year":1990,
            "email": "jane.Test@example.com",
            "telephone": "123456789",
            "language": "en",
            "presentation": "Hello, I am Jane",
            "supporting_person_id": None,
        }

        response = self.client.post(url, data, format="json")

        print("STATUS:", response.status_code)
        print("CONTENT:", response.content.decode())

        self.assertEqual(response.status_code, 201,msg=response.content.decode())
        # self.assertEqual(response.data["first_name"], "Jane")
        data = json.loads(response.content)
        self.assertEqual(data["first_name"], "Jane")

    def test_get_profile(self):
        url = f"/api/preferences/{self.user_profile.id}/"
        response = self.client.get(url)
        print("STATUS:", response.status_code)
        print("CONTENT:", response.content.decode())

        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.data["email"], "john.doe@example.com")
        data = json.loads(response.content)
        self.assertEqual(data["first_name"], "Jane")

    # def test_update_profile(self):
    #     url = f"/api/preferences/{self.user_profile.id}/"

    #     data = {
    #         "first_name": "Jonathan",
    #         "last_name": "Doe",
    #         "email": "jonathan.doe@example.com",
    #         "language": "sv",
    #     }
    #     response = self.client.patch(url, data, format="json")
    #     self.assertEqual(response.status_code, 200)
    #     # self.assertEqual(response.data["first_name"], "Jonathan")
    #     data = json.loads(response.content)
    #     self.assertEqual(data["first_name"], "Jane")

    # def test_delete_profile(self):
    #     url = f"/api/preferences/{self.user_profile.id}/"
    #     response = self.client.delete(url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data["success"], True)

    # def test_create_profile_with_existing_uno(self):
    #     url = "/api/preferences/"
    #     data = {
    #         "uno": "12345",  # Already exists
    #         "first_name": "Mark",
    #         "last_name": "Twain",
    #         "sex": "M",
    #         "birthday": "1985-06-15",
    #         "email": "mark.twain@example.com",
    #         "telephone": "987654321",
    #         "language": "en",
    #         "presentation": "Hello, I am Mark",
    #         "supporting_person_id": None,
    #     }

    #     response = self.client.post(url, data, format="json")
    #     self.assertIn(response.status_code, [400, 422])  # Accept both 400 and 422
    #     print("CONTENT:", response.content.decode())  # Debugging
    #     self.assertIn("UNO already exists", str(response.content.decode()))
  