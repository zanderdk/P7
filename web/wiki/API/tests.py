from django.test import TestCase, Client

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

    def test_max_count_works_alternative_method(self):
        max = 1
        response = self.client.get('/links/' + str(max))
        # check if 200
        self.assertEqual(response.status_code, 200)

        json = response.json()

        self.assertTrue(len(json) == max)

class TestPostReviews(TestCase):
    def setUp(self):
        self.client = Client()

    def test_must_be_post(self):
        response = self.client.put('/review')
        self.assertEqual(response.status_code, 405)

    def test_missing_status(self):
        response = self.client.post('/review', {"source":"123", "target":"345"})
        self.assertEqual(response.status_code, 400)

    def test_missing_source(self):
        response = self.client.post('/review', {"status":"bad", "target":"345"})
        self.assertEqual(response.status_code, 400)

    def test_missing_target(self):
        response = self.client.post('/review', {"source":"123", "status":"good"})
        self.assertEqual(response.status_code, 400)

    def test_success(self):
        response = self.client.post('/review', {"source":"123", "target":"345", "status": "good"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.content, b"Review Accepted")

    def test_wrong_status(self):
        response = self.client.post('/review', {"source":"123", "target":"345", "status": "nan"})
        self.assertEqual(response.status_code, 400)