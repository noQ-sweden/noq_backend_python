import sys
sys.path.append("....backend") # Adds folder where backend is to python modules path.
import json
from django.test import TestCase
from backend.models import (Host, Client, Product, Region, Available, Booking, State, BookingStatus)
from .test_data import TestData
from datetime import datetime, timedelta

class TestProductsApi(TestCase):
    t_data = None


    def setUp(self):
        self.t_data = TestData()
        # log in host user for the tests
        self.t_data.user_login(user_group="host", nr_of_users=1)


    def test_list_all_products(self):
        products_count = Product.objects.all().count()
        response = self.t_data.test_client.get("/api/host/products")

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        count = len(data)
        self.assertEqual(count, products_count)


    def test_list_host_products(self):
        host = Host.objects.all().first()
        products_count = Product.objects.filter(host_id=host.id).count()
        url = "/api/host/hosts/" + str(host.id) + "/products"
        response = self.t_data.test_client.get(url)

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        count = len(data)
        self.assertEqual(count, products_count)


    def test_get_unique_product(self):
        product = Product.objects.all().first()
        url = "/api/host/products/" + str(product.id)
        response = self.t_data.test_client.get(url)

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(product.id, data['id'])
        self.assertEqual(product.name, data['name'])
        self.assertEqual(product.description, data['description'])
        self.assertEqual(product.total_places, data['total_places'])

    '''
    # TODO: Fix Unprocessable Entity: /api/host/products issue with this test case
    def test_create_product(self):
        products_count = Product.objects.all().count()
        expected_count = products_count + 1

        url = "/api/host/products"
        data = {
            "id": 0,
            "name": "room",
            "description": "3-bäddrum",
            "total_places": 3,
            "host": {
                "region": {
                    "id": 1,
                    "name": "Malmö"
                },
                "id": 1,
                "name": "Host 1",
                "street": "Testaregatan 10",
                "postcode": "313 13",
                "city": "Malmö"
            },
            "type": "room"
        }
        response = self.t_data.test_client.post(url, data, content_type='application/json')

        self.assertEqual(response.status_code, 201)

        self.assertEqual(Product.objects.all().count(), expected_count)
    '''


    def test_update_product(self):
        product = Product.objects.all().first()

        places = product.total_places

        url = "/api/host/products/" + str(product.id) + "/edit"
        new_total_places = places * 2
        data = {
            "id": product.id,
            "name": "room",
            "description": "3-bäddrum",
            "total_places": new_total_places,
            "host": {
                "region": {
                    "id": 1,
                    "name": "Malmö"
                },
                "id": 1,
                "name": "Host 1",
                "street": "",
                "postcode": "",
                "city": "Malmö",
                "caseworkers": [
                    0
                    ]
            },
            "type": "room"
        }
        headers = {'Content-Type': 'application/json', 'accept': 'application/json'}
        response = self.t_data.test_client.put(url, json.dumps(data), headers=headers)

        self.assertEqual(response.status_code, 200)

        product = Product.objects.all().first()
        self.assertEqual(product.total_places, new_total_places)


    def test_delete_product(self):
        # Clean up existing data
        Booking.objects.all().delete()
        Available.objects.all().delete()
      
        product = self.t_data.products[0]  # Use the first product from the TestData

        # Step 2: Create bookings and availability for the product
        client = Client.objects.create(
            first_name="Test Client", gender="K", user=self.t_data.users[0], region=self.t_data.region
        )
        booking_status = BookingStatus.objects.get(id=State.PENDING)

        # Create a booking linked to the product
        booking = Booking.objects.create(
            product=product,
            user=client,
            status=booking_status,
            start_date=datetime.now().date(),
            end_date=datetime.now().date() + timedelta(days=1),
        )
        
        # Create availability for the product
        availability = Available.objects.create(
            product=product,
            available_date=datetime.now().date(),
            places_left=product.total_places -1,  # Assuming 1 place is booked
        )

        # Ensure the product has bookings and availability
        self.assertEqual(Booking.objects.count(), 1)

        #self.assertEqual(Available.objects.filter(product=product).count(), 1)
        availability = Available.objects.filter(product=product).first()
        self.assertEqual(availability.places_left, 1)

        # Step 3: Perform the DELETE request to delete the product
        url = f"/api/host/products/{product.id}"
        response = self.t_data.test_client.delete(url)

        # Step 4: Verify the response status is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Step 5: Ensure the product is deleted
        product_exists = Product.objects.filter(id=product.id).exists()
        self.assertFalse(product_exists)  # Product should no longer exist

        # Step 6: Ensure that the related bookings and availability are also affected
        booking_exists = Booking.objects.filter(product_id=product.id).exists()
        self.assertFalse(booking_exists)  # Booking should no longer exist

        availability_exists = Available.objects.filter(product_id=product.id).exists()
        self.assertFalse(availability_exists)  # Availability should no longer exist

        availability_exists = Available.objects.filter(product_id=product.id).exists()
        self.assertFalse(availability_exists)  # Availability should no longer exist



    def tearDown(self):
        # After the tests delete all data generated for the tests
        self.t_data.delete_users()
        self.t_data.delete_products()