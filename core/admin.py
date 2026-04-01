from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ContactMessage, LostItem, FoundItem

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('UoM Info', {'fields': ('role', 'student_id', 'phone')}),
    )
    list_display = ['username', 'email', 'role', 'is_staff']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['subject', 'name', 'email', 'submitted_at', 'is_read']
    list_filter = ['is_read']
    search_fields = ['name', 'email', 'subject']
    readonly_fields = ['name', 'email', 'subject', 'message', 'submitted_at', 'user']
    ordering = ['-submitted_at']

    def has_add_permission(self, request):
        return False

@admin.register(LostItem)
class LostItemAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'category', 'user', 'date_lost', 'status', 'submitted_at']
    list_filter = ['category', 'status']
    search_fields = ['item_name', 'user__username', 'last_seen']
    readonly_fields = ['user', 'submitted_at']
    list_editable = ['status']
    ordering = ['-submitted_at']

@admin.register(FoundItem)
class FoundItemAdmin(admin.ModelAdmin):
    list_display  = ['item_name', 'category', 'user', 'date_found', 'status', 'submitted_at']
    list_filter   = ['category', 'status']
    search_fields = ['item_name', 'user__username', 'found_at']
    readonly_fields = ['user', 'submitted_at']
    list_editable = ['status']
    ordering      = ['-submitted_at']