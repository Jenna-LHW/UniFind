from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ContactMessage, LostItem, FoundItem
from .models import Review, ReviewReply, ReviewLike, Claim


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

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display  = ['user', 'rating', 'is_banned', 'created_at']
    list_filter   = ['rating', 'is_banned']
    search_fields = ['user__username', 'comment']
    readonly_fields = ['user', 'rating', 'comment', 'created_at']
    list_editable = ['is_banned']
    ordering      = ['-created_at']

    def has_add_permission(self, request):
        return False

@admin.register(ReviewReply)
class ReviewReplyAdmin(admin.ModelAdmin):
    list_display  = ['review', 'admin', 'created_at']
    readonly_fields = ['review', 'created_at']
    ordering      = ['-created_at']

@admin.register(ReviewLike)
class ReviewLikeAdmin(admin.ModelAdmin):
    list_display  = ['user', 'review']
    readonly_fields = ['user', 'review']

@admin.action(description='Verify and Mark as Returned')
def mark_returned(modeladmin, request, queryset):
    queryset.update(status='returned')
    # Note: The browse views are filtered to exclude items with 'returned' claims
    
@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ['claimer', 'get_item_name', 'status', 'created_at']
    list_filter = ['status']
    actions = [mark_returned]

    def get_item_name(self, obj):
        item = obj.lost_item or obj.found_item
        return item.item_name
    get_item_name.short_description = 'Item'