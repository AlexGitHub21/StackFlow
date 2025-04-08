from app import app, db, add_new_inventory, update_quantity, record_location, record_inventory
# from unittest.mock import patch
import pytest

from test_base import BaseTestCase


def test_record_location():
    with app.app_context():
        assert record_location("New York") is True


def test_record_location_duplicate():
    with app.app_context():
        record_location("Tokyo")
        assert record_location("Tokyo") is False


def test_record_inventory():
    with app.app_context():
        assert record_inventory(1, 1, 5) == 15


# интеграционные
class Test(BaseTestCase):
    def test_add_product(self):
        with app.app_context():
            response = self.client.post("/add_product", data={
                "name": "TestProduct",
                "description": "Test",
                "price": "10.5"
            }, follow_redirects=True)
            assert response.status_code == 200
            assert b'TestProduct' in response.data

    def test_get_location(self):
        with app.app_context():
            response = self.client.get("/get_locations")
            self.assert200(response)
            self.assertEqual(response.json, {
                'locations': [
                    {'id': 1, 'name': 'Ижевск'},
                    {'id': 2, 'name': 'New York'},
                    {'id': 3, 'name': 'Tokyo'}
                ]}
            )

    def test_reduce_quantity(self):
        with app.app_context():
            response = self.client.post("/reduce_quantity", json={
                "product_id": 1,
                "location": "New York",
                "quantity": -1
            })
            assert response.status_code == 400
            assert response.get_json() == {
                "success": False,
                "error": "Количество товара не мб отрицательным"
            }
