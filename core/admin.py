from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ContactMessage

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('UoM Info', {'fields': ('role', 'student_id', 'phone')}),
    )
    list_display = ['username', 'email', 'role', 'is_staff']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display  = ['subject', 'name', 'email', 'submitted_at', 'is_read']
    list_filter   = ['is_read']
    search_fields = ['name', 'email', 'subject']
    readonly_fields = ['name', 'email', 'subject', 'message', 'submitted_at', 'user']
    ordering      = ['-submitted_at']

    def has_add_permission(self, request):
        return False