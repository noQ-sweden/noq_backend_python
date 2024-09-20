import sys
sys.path.append("....backend") # Adds folder where backend is to python modules path.
import json
from django.test import TestCase
from backend.models import Host, Client, Product, Region
from .test_data import TestData

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
        product = Product.objects.all().first()
        id = product.id

        url = "/api/host/products/" + str(product.id)
        # data should be product_id, not sure how to use parameter
        response = self.t_data.test_client.delete(url, product_id=id)

        self.assertEqual(response.status_code, 200)

        product = Product.objects.all().first()
        self.assertNotEqual(product.id, id)


    def tearDown(self):
        # After the tests delete all data generated for the tests
        self.t_data.delete_users()
        self.t_data.delete_products()