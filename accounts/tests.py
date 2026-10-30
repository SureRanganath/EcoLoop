from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import UserProfile


class EnsureUserProfileSignalTests(TestCase):

    def test_new_user_gets_default_profile(self):
        user = User.objects.create_user(username='newbie', password='TestPass@123',
                                        first_name='New', last_name='Bee')
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.role, 'buyer')
        self.assertEqual(profile.company_name, 'New Bee')

    def test_superuser_gets_profile(self):
        user = User.objects.create_superuser('root', 'root@test.com', 'TestPass@123')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_resaving_user_does_not_duplicate_or_alter_profile(self):
        user = User.objects.create_user(username='stable', password='TestPass@123')
        UserProfile.objects.filter(user=user).update(role='supplier', company_name='ACME')
        user.email = 'changed@test.com'
        user.save()
        self.assertEqual(UserProfile.objects.filter(user=user).count(), 1)
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.role, 'supplier')
        self.assertEqual(profile.company_name, 'ACME')

    def test_user_without_profile_is_healed_on_save(self):
        user = User.objects.create_user(username='orphan', password='TestPass@123')
        UserProfile.objects.filter(user=user).delete()
        self.assertFalse(UserProfile.objects.filter(user=user).exists())
        user.save()
        self.assertTrue(UserProfile.objects.filter(user=user).exists())


class DashboardProfileTests(TestCase):

    def test_dashboard_loads_for_user_created_without_profile_details(self):
        """A user created straight in the admin (no explicit profile data)
        must still reach /dashboard/ instead of the 'Profile not found' path."""
        user = User.objects.create_superuser('adminuser', 'a@test.com', 'TestPass@123')
        self.client.force_login(user)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')

    def test_registration_stores_real_profile_fields(self):
        """RegisterForm must overwrite the signal's placeholder profile with
        the submitted role/company details rather than erroring on duplicates."""
        form_data = {
            'username': 'reguser', 'first_name': 'Reg', 'last_name': 'User',
            'email': 'reg@test.com',
            'password1': 'Str0ngPass!23', 'password2': 'Str0ngPass!23',
            'role': 'supplier', 'company_name': 'Reg Industries',
            'industry_type': 'Manufacturing', 'phone': '9000000000',
            'city': 'Pune', 'state': 'Maharashtra',
        }
        response = self.client.post(reverse('register'), data=form_data)
        self.assertEqual(response.status_code, 302)
        profile = UserProfile.objects.get(user__username='reguser')
        self.assertEqual(profile.role, 'supplier')
        self.assertEqual(profile.company_name, 'Reg Industries')
        self.assertEqual(profile.city, 'Pune')
