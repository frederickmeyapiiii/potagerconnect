import unittest
from app import create_app


class PotagerAppTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'PotagerConnect', response.data)
        self.assertIn(b'M\xc3\xa9t\xc3\xa9o', response.data)
        self.assertIn(b'Partage des r\xc3\xa9coltes', response.data)

    def test_api_plots(self):
        response = self.client.get('/api/plots')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

    def test_api_posts(self):
        response = self.client.get('/api/posts')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)


if __name__ == '__main__':
    unittest.main()
