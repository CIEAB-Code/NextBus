import unittest
import data_functions
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
        data = data_functions.get_bus_info()
        self.assertIsNotNone(data)

    def test_query_data(self):
        formatted_data = data_functions.query_data()
        self.assertIsNotNone(formatted_data)

    def test_filter_morning(self):
        formatted_data = data_functions.filter_morning(data_functions.query_data())
        self.assertIsNotNone(formatted_data)

    def test_filter_afternoon(self):
        formatted_data = data_functions.filter_afternoon(data_functions.query_data())
        self.assertIsNotNone(formatted_data)

    def test_filter_evening(self):
        formatted_data = data_functions.filter_evening(data_functions.query_data())
        self.assertIsNotNone(formatted_data)


if __name__ == '__main__':
    unittest.main()
