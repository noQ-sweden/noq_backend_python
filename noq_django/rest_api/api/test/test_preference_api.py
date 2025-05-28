from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client as TestClient
from datetime import datetime, date
import json
import base64

from backend.models import Client, UserProfile, Region  # Add Region here



class TestUserProfileAPI(TestCase):
    def auth_headers(self):
        credentials = f"{self.username}:{self.password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {"HTTP_AUTHORIZATION": f"Basic {encoded}"}

    def setUp(self):
    # Setup test user
        self.username = "testuser@example.com"
        self.password = "securepass123"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com"
        )
        self.test_region = Region.objects.create(name="Test Region")
     # Setup client object with a unokod value
        self.test_client_obj = Client.objects.create(
                user=self.user,
                first_name="Test Client",
                unokod="12345",
                gender="M",
                region=self.test_region
        )

    # Create a test profile
        self.user_profile = UserProfile.objects.create(
          user=self.user,
          client=self.test_client_obj,
          language="en",
          presentation="Hello, I am John"
       )

        self.client = TestClient()
        self.client.login(username=self.username, password=self.password)

    def test_list_profiles(self):
        """Test getting all profiles"""
        response = self.client.get("/api/preferences/", **self.auth_headers())
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["first_name"], self.user.first_name)

    def test_get_profile(self):
        """Test getting a specific profile"""
        response = self.client.get(f"/api/preferences/{self.user.id}", **self.auth_headers())
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["first_name"], self.user.first_name)
        self.assertEqual(data["last_name"], self.user.last_name)
        self.assertEqual(data["email"], self.user.email)
        self.assertEqual(data["uno"], self.test_client_obj.unokod)


    def test_get_profile_unauthorized(self):
        """Test getting another user's profile (should fail)"""
        other_user = User.objects.create_user(username="other@example.com", password="pass123")
        response = self.client.get(f"/api/preferences/{other_user.id}", **self.auth_headers())
        self.assertEqual(response.status_code, 403)

    def test_create_profile(self):
        """Test creating a new profile"""
        self.user_profile.delete()
        region = Region.objects.create(name="Another Region")
        new_user = User.objects.create_user(
            username="jane@example.com",
            password="securepass123",
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com"
        )

        new_client = Client.objects.create(
              first_name="Another Client",
              unokod="54321",
              gender="F",
              region=region 
        )

        new_profile = UserProfile.objects.create(
             user=new_user,
             client=new_client,
             language="en",
             presentation="Hello, I am Jane"
        )

        self.assertEqual(new_profile.user.first_name, "Jane")
        self.assertEqual(new_profile.client.unokod, "54321")
    # def test_create_profile_duplicate_uno(self):
    #     """Test creating a profile with duplicate UNO (should fail)"""
    #     new_data = {
    #         "uno": "12345",  # Same UNO as existing profile
    #         "first_name": "Jane",
    #         "last_name": "Smith",
    #         "email": "jane@example.com",
    #         "sex": "F",
    #         "birthday": "1992-02-02",
    #         "birth_year": 1992,
    #         "telephone": "9876543210",
    #         "language": "en",
    #         "presentation": "Test presentation",
    #         "supporting_person_id": None
    #     }
    #     response = self.client.post(
    #         "/api/preferences/",
    #         data=json.dumps(new_data),
    #         content_type="application/json",
    #         **self.auth_headers()
    #     )
    #     self.assertEqual(response.status_code, 400)
    #     self.assertIn("Profile already exists", response.json()["detail"])

    def test_update_profile(self):
        """Test updating a profile"""
        self.user.first_name = "Johnny"
        self.user.last_name = "Updated"
        self.user.email = "johnny.updated@example.com"
        self.user.save()

        response = self.client.get(f"/api/preferences/{self.user.id}", **self.auth_headers())
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["first_name"], "Johnny")
        self.assertEqual(data["last_name"], "Updated")
        self.assertEqual(data["email"], "johnny.updated@example.com")

    def test_delete_profile(self):
        """Test deleting a profile"""
        response = self.client.delete(f"/api/preferences/{self.user.id}", **self.auth_headers())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["success"], True)
        self.assertEqual(UserProfile.objects.filter(user=self.user).count(), 0)

    def test_delete_profile_unauthorized(self):
        """Test deleting another user's profile (should fail)"""
        other_user = User.objects.create_user(username="other@example.com", password="pass123")
        other_profile = UserProfile.objects.create(user=other_user, client=self.test_client_obj)
        response = self.client.delete(f"/api/preferences/{other_user.id}", **self.auth_headers())
        self.assertEqual(response.status_code, 403)

    def tearDown(self):
        UserProfile.objects.all().delete()
        User.objects.all().delete()
        Client.objects.all().delete()