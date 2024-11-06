from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status

# TestCase.databases = {'default'}
fixtures = ['main.json']


# Create your tests here.
class UpcomingWebinarTestCase(APITestCase):

    def test_upcoming_webinar(self):
        response = self.client.get('/api/webinar/upcoming-webinar?offset=0&limit=100')
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
