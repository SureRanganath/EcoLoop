from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    ROLE_CHOICES = [('supplier', 'Supplier'), ('buyer', 'Buyer')]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    company_name = models.CharField(max_length=200)
    industry_type = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company_name} ({self.role})"

    @property
    def is_supplier(self):
        return self.role == 'supplier'

    @property
    def is_buyer(self):
        return self.role == 'buyer'


@receiver(post_save, sender=User)
def ensure_user_profile(sender, instance, created, raw, **kwargs):
    """Guarantee every user has a UserProfile.

    Profiles are normally created with explicit details (registration form,
    seed_data, tests). This signal covers users created without them — most
    commonly via the Django admin — which would otherwise break
    ``user.profile`` lookups in views and templates.
    """
    if raw:  # loading a fixture: let the fixture provide the profile
        return
    UserProfile.objects.get_or_create(
        user=instance,
        defaults={
            'role': 'buyer',
            'company_name': instance.get_full_name() or instance.username,
            'industry_type': 'Other',
            'city': '',
            'state': '',
        },
    )
