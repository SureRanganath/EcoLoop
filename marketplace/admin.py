from django.contrib import admin
from .models import MaterialCategory, WasteListing, PurchaseRequest, FavouriteListing, ContactMessage


@admin.register(MaterialCategory)
class MaterialCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(WasteListing)
class WasteListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'supplier', 'category', 'quantity', 'price_per_kg', 'status', 'city', 'state', 'created_at']
    list_filter = ['status', 'category', 'state', 'quality_grade']
    search_fields = ['title', 'description', 'supplier__username']
    list_editable = ['status']


@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ['buyer', 'listing', 'requested_quantity', 'status', 'created_at']
    list_filter = ['status']
    list_editable = ['status']


@admin.register(FavouriteListing)
class FavouriteListingAdmin(admin.ModelAdmin):
    list_display = ['user', 'listing', 'created_at']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at', 'is_read']
    list_editable = ['is_read']
