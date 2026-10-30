from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone


class MaterialCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='bi-recycle')
    color = models.CharField(max_length=20, default='success')

    class Meta:
        verbose_name_plural = 'Material Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class WasteListing(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('sold', 'Sold'),
        ('inactive', 'Inactive'),
    ]
    QUALITY_CHOICES = [
        ('A', 'Grade A - Excellent'),
        ('B', 'Grade B - Good'),
        ('C', 'Grade C - Fair'),
        ('D', 'Grade D - Poor'),
    ]

    supplier = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=200)
    category = models.ForeignKey(MaterialCategory, on_delete=models.PROTECT, related_name='listings')
    description = models.TextField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    quality_grade = models.CharField(max_length=1, choices=QUALITY_CHOICES, default='B')
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    image = models.ImageField(upload_to='listings/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.supplier.profile.company_name}"

    @property
    def total_value(self):
        return self.quantity * self.price_per_kg


class PurchaseRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchase_requests')
    listing = models.ForeignKey(WasteListing, on_delete=models.CASCADE, related_name='requests')
    requested_quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    proposed_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Request by {self.buyer.username} for {self.listing.title}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.requested_quantity and self.listing_id:
            if self.requested_quantity > self.listing.quantity:
                raise ValidationError('Requested quantity exceeds available quantity.')


class FavouriteListing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favourites')
    listing = models.ForeignKey(WasteListing, on_delete=models.CASCADE, related_name='favourited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'listing']

    def __str__(self):
        return f"{self.user.username} - {self.listing.title}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} from {self.name}"
