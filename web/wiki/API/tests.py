from django.test import TestCase, Client
    

# Create your tests here.
class TestGetLinks(TestCase):
    def setUp(self):
        self.client = Client()

    def test_not_empty_response(self):
        response = self.client.get('/links')
        # check if 200
        self.assertEqual(response.status_code, 200)

        json = response.json()

        self.assertTrue(len(json) > 0)

    def test_source_target_present(self):
        response = self.client.get('/links')
        # check if 200
        self.assertEqual(response.status_code, 200)

        json = response.json()
        print(json)
        for element in json:
            self.assertIn("source", element)
            self.assertIn("target", element)

    def test_max_count_works(self):
        max = 1
        response = self.client.get('/links?max=' + str(max))
        # check if 200
        self.assertEqual(response.status_code, 200)

        json = response.json()

        self.assertTrue(len(json) == max)