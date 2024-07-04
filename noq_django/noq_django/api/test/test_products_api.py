import sys
sys.path.append("....backend") # Adds folder where backend is to python modules path.
import json
from django.test import TestCase
from django.contrib.auth.models import User, Group
from backend.models import Host, Client, Product, Region
from django.test import Client
from ..host_api import router

class TestProductsApi(TestCase):
    user = None
    client = None
    username = "host"
    password = "hostpassword"

    def host_login(self):
        # Create host user for the tests if not existing
        if User.objects.filter(username=self.username).first() == None:
            self.user = User.objects.create_user(username=self.username, password=self.password)
            group_obj, created = Group.objects.get_or_create(name="host")
            self.user.groups.add(group_obj)

        # Login the host user
        self.client = Client(router)
        self.client.login(username=self.username, password=self.password)

    def delete_user(self):
        # Delete the user created for the tests
        user = User.objects.get(username=self.username)
        user.delete()

    def delete_products(self):
        # Delete all products created for the tests
        Product.objects.all().delete()
        Host.objects.all().delete()
        Region.objects.all().delete()

    def setUp(self):
        # log in host user for the tests
        self.host_login()
        # Create products that can be used during the tests
        if Product.objects.filter(id=1).first() == None:
            region = Region.objects.create(name="Malmö")
            hostA = Host.objects.create(name="Host 1", street="", postcode="", city="Malmö", region_id=region.id)
            hostB = Host.objects.create(name="Host 2", street="", postcode="", city="Malmö", region_id=region.id)
            productA = Product.objects.create(name="room", total_places=2, host_id=hostA.id, type="room")
            productB = Product.objects.create(name="room", total_places=5, host_id=hostB.id, type="room")
            productC = Product.objects.create(name="woman-only", total_places=3, host_id=hostB.id, type="woman-only")


    def test_list_all_products(self):
        products_count = Product.objects.all().count()
        response = self.client.get("/api/host/products")

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        count = len(data)
        self.assertEqual(count, products_count)

    def test_list_host_products(self):
        host = Host.objects.all().first()
        products_count = Product.objects.filter(host_id=host.id).count()
        url = "/api/host/hosts/" + str(host.id) + "/products"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        count = len(data)
        self.assertEqual(count, products_count)

    def test_get_unique_product(self):
        product = Product.objects.all().first()
        url = "/api/host/products/" + str(product.id)
        response = self.client.get(url)

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
        response = self.client.post(url, data, content_type='application/json')

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
                "city": "Malmö"
            },
            "type": "room"
        }
        headers = {'Content-Type': 'application/json', 'accept': 'application/json'}
        response = self.client.put(url, json.dumps(data), headers=headers)

        self.assertEqual(response.status_code, 200)

        product = Product.objects.all().first()
        self.assertEqual(product.total_places, new_total_places)

    def test_delete_product(self):
        product = Product.objects.all().first()
        id = product.id

        url = "/api/host/products/" + str(product.id)
        # data should be product_id, not sure how to use parameter
        response = self.client.delete(url, product_id=id)

        self.assertEqual(response.status_code, 200)

        product = Product.objects.all().first()
        self.assertNotEqual(product.id, id)

    def tearDown(self):
        # After the tests delete all data generated for the tests
        self.delete_user()
        self.delete_products()
