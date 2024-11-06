from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from apps.user.models import *
from rest_framework_simplejwt.tokens import RefreshToken


# Create your tests here.
class TestCaseBase(APITestCase):
    @property
    def bearer_token(self):
        # assuming there is a user in User model
        user = User.objects.get(username='jack')

        refresh = RefreshToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f'Bearer {refresh.access_token}'}


class CalendarListTest(APITestCase):
    def setUp(self):
        username = "jack"
        password = "1234"

        jwt_fetch_data = {
            'username': username,
            'password': password
        }
        # print(f"{jwt_fetch_data=}")
        # url = reverse('custom_token_obtain_pair')
        # response = self.client.post("/api/auth/login/", jwt_fetch_data)
        # print(response.content,"====")
        # token = response.data['access']
        # user = User.objects.get(username='jack')
        # refresh = RefreshToken.for_user(user)
        # token = refresh.access_token
        token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjgwMzQ5NTc2LCJpYXQiOjE2NzI0ODcxNzYsImp0aSI6IjRlZWExYWI3NjJmMzRhMThhZjZhNjFiMTE4NWQxZDJmIiwidXNlcl9pZCI6MTEsInVzZXJuYW1lIjoiamFjayIsInRpbm9kZV90b2tlbiI6bnVsbH0.ekyRuVtyq8qj__y5lIrLKUMHNNRhUAQYhNgw3biFlY8'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_get_results(self):
        # token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9' \
        #         '.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjc0MTI5OTYxLCJpYXQiOjE2NjYyNjc1NjEsImp0aSI6ImE0YzZkYjEzOTgwMjQ5MmU5MTAwNmJjOTYyZmY1MDg5IiwidXNlcl9pZCI6MTEsInVzZXJuYW1lIjoiamFjayIsInRpbm9kZV90b2tlbiI6bnVsbH0.gasdlqM4cYvQ9CDyA5jGSdRhQQjXq045WKyXPKPbIKs '
        # self.client.credentials(HTTP_AUTHORIZATION="Bearer " + str(token))
        response = self.client.get(reverse('get-calendar-list'))
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
