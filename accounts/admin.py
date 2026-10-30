from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'company_name', 'role', 'city', 'state', 'is_verified', 'created_at']
    list_filter = ['role', 'state', 'is_verified']
    search_fields = ['user__username', 'company_name', 'city']
    list_editable = ['is_verified']
