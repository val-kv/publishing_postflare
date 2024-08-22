from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Product

User = get_user_model()


class PostViewSetTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(phone_number='admin', password='password')
        self.normal_user = User.objects.create_user(phone_number='user', password='password')

        self.client.force_login(self.admin_user)
        self.post_data = {'title': 'Test Title', 'content': 'Test Content'}

    def test_create_post_as_admin(self):
        response = self.client.post(reverse('publishing:posts'), self.post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_posts_as_authenticated_user(self):
        self.client.force_login(self.normal_user)
        response = self.client.get(reverse('publishing:posts'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_post_as_normal_user(self):
        self.client.force_login(self.normal_user)
        response = self.client.post(reverse('publishing:posts'), self.post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserRegistrationTests(APITestCase):
    def setUp(self):
        self.user_data = {'phone_number': '1234567890', 'password': 'testpassword'}

    def test_user_registration(self):
        response = self.client.post(reverse('publishing:register'), self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

    def test_user_registration_invalid(self):
        response = self.client.post(reverse('publishing:register'), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number='user', password='password')
        self.login_data = {'phone_number': 'user', 'password': 'password'}

    def test_successful_login(self):
        response = self.client.post(reverse('publishing:login'), self.login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Успешный вход')

    def test_failed_login(self):
        login_data_wrong = {'phone_number': 'wrong', 'password': 'wrong'}
        response = self.client.post(reverse('publishing:login'), login_data_wrong)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserLogoutTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number='user', password='password')
        self.client.force_login(self.user)

    def test_logout(self):
        response = self.client.post(reverse('publishing:logout'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Успешный выход')


class CreateCheckoutSessionTests(APITestCase):
    def setUp(self):
        self.product = Product.objects.create(name='Test Product', price=1000)

    def test_create_checkout_session(self):
        response = self.client.post(reverse('publishing:create-checkout-session', kwargs={'pk': self.product.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.json())


