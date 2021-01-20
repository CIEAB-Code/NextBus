import unittest
import nextbus
import requests


class TestNextBus(unittest.TestCase):
    def setUp(self):
        requests.get('http://localhost:5000')
        
    def test_homepage(self):
        response = requests.get('http://localhost:5000')
        self.assertEqual(response.status_code, 200)

    def test_datapage(self):
        response = requests.get('http://localhost:5000/data/')
        self.assertEqual(response.status_code, 200)

    def test_get_bus_info(self):
        data = nextbus.get_bus_info()
        self.assertIsNotNone(data)

    def test_query_data(self):
        formatted_data = nextbus.query_data()
        self.assertIsNotNone(formatted_data)

    def test_filter_morning(self):
        formatted_data = nextbus.filter_morning(nextbus.query_data())
        self.assertIsNotNone(formatted_data)

    def test_filter_afternoon(self):
        formatted_data = nextbus.filter_afternoon(nextbus.query_data())
        self.assertIsNotNone(formatted_data)

    def test_filter_evening(self):
        formatted_data = nextbus.filter_evening(nextbus.query_data())
        self.assertIsNotNone(formatted_data)


if __name__ == '__main__':
    unittest.main()
