# from django.test import TestCase
# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APIClient
# from rest_framework_simplejwt.tokens import RefreshToken
# from backend.models import UserProfile, User


# class UserProfileAPITestCase(TestCase):
    
#     def setUp(self):
#         # Create a user for the test
#         self.user = User.objects.create_user(username="testuser", password="password123")
        
#         # Create a refresh token for the user (JWT)
#         refresh = RefreshToken.for_user(self.user)
#         self.token = str(refresh.access_token)

#         # Create a client instance and set the authorization header
#         self.client = APIClient()
#         self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        
#         # Create a user profile for the test user
#         self.user_profile = UserProfile.objects.create(
#             user=self.user,
#             uno="12345",
#             first_name="John",
#             last_name="Doe",
#             email="john.doe@example.com",
#             sex="M",
#             birthday="1990-01-01",
#             birth_year=1990,
#             language="en",
#             presentation="Hello, I am John",
#         )

#     def test_create_profile(self):
#         url = reverse("preferences:create-profile") # Update this with the correct Ninja path
#         data = {
#             "uno": "54321",
#             "first_name": "Jane",
#             "last_name": "Smith",
#             "sex": "F",
#             "birthday": "1992-02-02",
#             "birth_year":1992,
#             "email": "jane.smith@example.com",
#             "telephone": "123456789",
#             "language": "en",
#             "presentation": "Hello, I am Jane",
#             "supporting_person_id": None,
#         }

#         response = self.client.post(url, data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(response.data["first_name"], "Jane")

#     def test_get_profile(self):
#         url = reverse("get-profile", kwargs={"user_id": self.user.id})  # Update with correct Ninja path
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["email"], "john.doe@example.com")

#     def test_update_profile(self):
#         url = reverse("update-profile", kwargs={"user_id": self.user.id})  # Update with correct Ninja path

#         data = {
#             "first_name": "Jonathan",
#             "last_name": "Doe",
#             "email": "jonathan.doe@example.com",
#             "language": "sv",
#         }
#         response = self.client.patch(url, data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["first_name"], "Jonathan")

#     def test_delete_profile(self):
#         url = reverse("delete-profile", kwargs={"user_id": self.user.id})  # Update with correct Ninja path
#         response = self.client.delete(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["success"], True)

#     def test_create_profile_with_existing_uno(self):
#         url = reverse("create-profile")  # Update with correct Ninja path
#         data = {
#             "uno": "12345",  # Already used UNO
#             "first_name": "Mark",
#             "last_name": "Twain",
#             "sex": "M",
#             "birthday": "1985-06-15",
#             "birth_year":1985,
#             "email": "mark.twain@example.com",
#             "telephone": "987654321",
#             "language": "en",
#             "presentation": "Hello, I am Mark",
#             "supporting_person_id": None,
#         }

#         response = self.client.post(url, data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("UNO already exists", str(response.data))
from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client as TestClient
from rest_framework import status
from datetime import datetime
import json
import base64

from backend.models import UserProfile


class TestUserProfileAPI(TestCase):
    def auth_headers(self):
        credentials = f"{self.username}:{self.password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {"HTTP_AUTHORIZATION": f"Basic {encoded}"}

    def setUp(self):
        # Setup a test user
        self.username = "testuser@example.com"
        self.password = "securepass123"
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.client = TestClient()
        self.client.login(username=self.username, password=self.password)

        # Example of creating a user profile (adjust according to your model)
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

    def test_create_user_profile(self):
        # Testing the creation of a user profile
        new_data = {
            "uno": "54321",
            "first_name": "Jane",
            "last_name": "Smith",
            "sex": "F",
            "birthday": "1992-02-02",
            "birth_year":1992,
            "email": "jane.smith@example.com",
            "telephone": "123456789",
            "language": "en",
            "presentation": "Hello, I am Jane",
            "supporting_person_id": None,
        }
        response = self.client.post(
            "/api/preferences/create-profile/",
            data=json.dumps(new_data),
            content_type="application/json",
            **self.auth_headers()
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["first_name"], "Jane")
