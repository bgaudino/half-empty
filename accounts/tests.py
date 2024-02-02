from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from . import models

User = get_user_model()


class ProfileTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@test.com', password='password')
        self.client.login(email=self.user.email, password='password')

    def test_user_with_no_profile_redirected_to_create_view(self):
        res = self.client.get(reverse('profile_detail'))
        self.assertRedirects(res, reverse('profile_create'))

    def test_user_with_profile_not_redirected(self):
        models.Profile.objects.create(user=self.user, full_name='Test User')
        res = self.client.get(reverse('profile_detail'))
        self.assertEqual(res.status_code, 200)
