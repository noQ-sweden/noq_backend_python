import sys
sys.path.append("....backend") # Adds folder where backend is to python modules path.
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from backend.models import Region, Host, Product, Client, Booking, BookingStatus, State, Available
from datetime import date, datetime, timedelta
import json
from django.test import Client as TestClient
from ..caseworker_api import router

class CaseworkerCRUDUserTests(TestCase):
   caseworker_user = None
   caseworker_name = "user.caseworker@test.nu"
   user_name_one = "user.user1@test.nu"
   password = "VeryBadPassword!"

   def create_user(self, username, group):
      user = User.objects.create_user(username=username, password=self.password)
      group_obj, created = Group.objects.get_or_create(name=group)
      user.groups.add(group_obj)

   def caseworker_login(self):
      # Create host user and client users for the test
      if User.objects.filter(username=self.caseworker_name).first() == None:
            client_user_one = self.create_user(self.user_name_one, "user")
            caseworker_user = self.create_user(self.caseworker_name, "caseworker")

      # Login the caseworker
      self.client = TestClient(router)
      self.client.login(username=self.caseworker_name, password=self.password)
      print(self.client)


   def delete_users(self):
      # Delete the host_user created for the tests
      users = User.objects.all().delete()


   def delete_products(self):
      # Delete all products created for the tests
      Product.objects.all().delete()
      Available.objects.all().delete()
      Host.objects.all().delete()
      Region.objects.all().delete()

   def setUp(self):

      self.caseworker_login()

      self.region = Region.objects.create(name="Göteborg")
      
      # Data för att skapa en ny användare
      self.user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "password": "Password123",
            "phone": "123456789",
            "gender": "M",
            "street": "Main Street",
            "postcode": "12345",
            "city": "Somewhere",
            "region": self.region.id,
            "country": "Sweden",
            "day_of_birth": "1990-01-01",
            "personnr_lastnr": "1234"
      }
      client = Client.objects.create(
               first_name="John",
               last_name="Doe",
               gender="M",
               street="123 Main St",
               postcode="12345",
               city="New York",
               country="USA",
               phone="123-456-7890",
               email="john.doe@example.com",
               unokod="ABC123",
               day_of_birth=datetime.now().date() + timedelta(weeks=-1500),
               personnr_lastnr="1234",
               region=self.region,
               requirements=None,
               last_edit=datetime.now().date(),
               user=User.objects.filter(username=self.user_name_one).first(),
            ) 

   def test_register_user(self):
      """Test for creating (registering) a new user"""
      """Email must exist"""
      """Region must exist"""
      """day_of_birth must exist with correct format"""

      user_data = {
         "first_name": "John",
         "last_name": "Doe",
         "email": "john@example.com",
         "password": "Password123",
         "phone": "123456789",
         "gender": "M",
         "street": "Main Street",
         "postcode": "12345",
         "city": "Somewhere",
         "region": self.region.id,
         "country": "Sweden",
         "day_of_birth": "1990-01-01",
         "personnr_lastnr": "1234"
      }
      url = '/api/caseworker/register'
      response = self.client.post(url, data=json.dumps(user_data), content_type='application/json')
      
      response_data = json.loads(response.content)
      self.assertEqual(response.status_code, 201)
      self.assertEqual(response_data["success"], "Användare registrerad!")
      self.assertIn("user_id", response_data)
      self.assertGreater(response_data["user_id"], 0)

    
   def test_get_user_information(self):
      """Test for retrieving user information by user ID"""       

      # Fetch created user
      user_one = User.objects.filter(username=self.user_name_one).first()
      # Retrieve the associated client
      client_one = Client.objects.filter(user=user_one).first()
      self.assertIsNotNone(client_one, "Client should exist for the user")
      # Send GET request to retrieve user information
      response = self.client.get(f"/api/caseworker/user/{user_one.id}")
      self.assertEqual(response.status_code, 200)
      response_data = json.loads(response.content)

      # Check if the response data matches the client's information
      self.assertEqual(response_data["email"], client_one.email)
      self.assertEqual(response_data["first_name"], client_one.first_name)
      self.assertEqual(response_data["last_name"], client_one.last_name)
      self.assertEqual(response_data["region"], self.region.id)

   def test_update_user(self):
      """Test for updating user information"""

      user_one = User.objects.filter(username=self.user_name_one).first()
      client_one = Client.objects.filter(user=user_one).first()
      
      updated_data = {
         "first_name": "Jane",
         "last_name": "Smith",
         "email": "jane@example.com",
         "phone": "987654321",
         "gender": "F",
         "street": "Updated Street",
         "postcode": "54321",
         "city": "Updated City",
         "region": self.region.id,
         "country": "Updated Country",
         "day_of_birth": "1985-05-05",
         "personnr_lastnr": "5678"
      }

      url = f'/api/caseworker/update/user/{user_one.id}'
      response = self.client.put(url, data=json.dumps(updated_data), content_type='application/json')

      self.assertEqual(response.status_code, 200)

      response_data = json.loads(response.content)

      self.assertEqual(response_data['first_name'], updated_data['first_name'])
      self.assertEqual(response_data['last_name'], updated_data['last_name'])

      self.assertNotEqual(client_one.first_name, response_data['first_name'])
      self.assertNotEqual(client_one.last_name, response_data['last_name'])
   
   def test_delete_user(self):
    """Test for deleting a user by user ID"""

    user_one = User.objects.filter(username=self.user_name_one).first()
    url = f"/api/caseworker/delete/user/{user_one.id}"

    # Send DELETE request to the API
    response = self.client.delete(url, content_type='application/json')

    # Ensure response status is 200 OK
    self.assertEqual(response.status_code, 200)
    response_data = json.loads(response.content)

    self.assertIn('message', response_data)
    self.assertEqual(response_data['message'], "Användaren har tagits bort.")

    # Try to fetch user information after deletion
    response = self.client.get(f"/api/caseworker/user/{user_one.id}")
    self.assertEqual(response.status_code, 404)  

   def test_register_no_password(self):
      """Password must exist"""

      user_data = {
         "first_name": "",
         "last_name": "",
         "email": "test@noq.nu", # Have to exist
         "password": "",# Have to exist
         "phone": "",
         "gender": "",
         "street": "",
         "postcode": "",
         "city": "",
         "region": self.region.id,# Have to exist
         "country": "",
         "day_of_birth": "1990-01-01", # Have to exist
         "personnr_lastnr": ""
      }
      url = '/api/caseworker/register'
      response = self.client.post(url, data=json.dumps(user_data), content_type='application/json')
      response_data = json.loads(response.content)
      self.assertEqual(response.status_code, 400)
      self.assertEqual(response_data["error"], "Lösenord måste anges och får inte vara tomt.")

   def test_register_no_email(self):
      """Email must exist"""

      user_data = {
         "first_name": "",
         "last_name": "",
         "email": "", # Have to exist
         "password": "testpassword",# Have to exist
         "phone": "",
         "gender": "",
         "street": "",
         "postcode": "",
         "city": "",
         "region": self.region.id, # Have to exist
         "country": "",
         "day_of_birth": "1990-01-01", # Have to exist
         "personnr_lastnr": ""
      }
      url = '/api/caseworker/register'
      response = self.client.post(url, data=json.dumps(user_data), content_type='application/json')
      response_data = json.loads(response.content)

      self.assertEqual(response.status_code, 400)
      self.assertEqual(response_data["error"], "e-post måste anges och får inte vara tom.")

   def test_register_no_region(self):
      """Region must exist"""

      user_data = {
         "first_name": "",
         "last_name": "",
         "email": "test@noq.nu", # Have to exist
         "password": "testpassword",# Have to exist
         "phone": "",
         "gender": "",
         "street": "",
         "postcode": "",
         "city": "",
         "region": "", # Have to exist
         "country": "",
         "day_of_birth": "1990-01-01", # Have to exist
         "personnr_lastnr": ""
      }
      url = '/api/caseworker/register'
      response = self.client.post(url, data=json.dumps(user_data), content_type='application/json')
      response_data = json.loads(response.content)
      self.assertEqual(response.status_code, 422)
 

   def test_register_no_day_of_birth(self):
      """day_of_birth must exist with correct format"""

      user_data = {
         "first_name": "",
         "last_name": "",
         "email": "test@noq.nu", # Have to exist
         "password": "testpassword",
         "phone": "",
         "gender": "",
         "street": "",
         "postcode": "",
         "city": "",
         "region": self.region.id, # Have to exist
         "country": "",
         "day_of_birth": "", # Have to exist in the correct format
         "personnr_lastnr": ""
      }
      url = '/api/caseworker/register'
      response = self.client.post(url, data=json.dumps(user_data), content_type='application/json')
      self.assertEqual(response.status_code, 422)


   def test_update_no_region(self):
      """Region must exist"""

      user_data = {
         "first_name": "",
         "last_name": "",
         "email": "test@noq.nu", 
         "password": "testpassword",
         "phone": "",
         "gender": "",
         "street": "",
         "postcode": "",
         "city": "",
         "region": "", # Have to exist
         "country": "",
         "day_of_birth": "1990-01-01", # Have to exist
         "personnr_lastnr": ""
      }
      url = '/api/caseworker/register'
      response = self.client.post(url, data=json.dumps(user_data), content_type='application/json')
      response_data = json.loads(response.content)
      self.assertEqual(response.status_code, 422)


   def test_update_no_day_of_birth(self):
      """day_of_birth must exist with correct format"""

      user_data = {
         "first_name": "",
         "last_name": "",
         "email": "test@noq.nu", # Have to exist
         "password": "testpassword",
         "phone": "",
         "gender": "",
         "street": "",
         "postcode": "",
         "city": "",
         "region": self.region.id, # Have to exist
         "country": "",
         "day_of_birth": "", # Have to exist in the correct format, xxxx-xx-xx
         "personnr_lastnr": ""
      }
      url = '/api/caseworker/register'
      response = self.client.post(url, data=json.dumps(user_data), content_type='application/json')
      self.assertEqual(response.status_code, 422)

   def tearDown(self):
      User.objects.all().delete()
      Client.objects.all().delete()
      Booking.objects.all().delete()
      Product.objects.all().delete()