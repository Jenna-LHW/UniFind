from rest_framework import serializers
from .models import LostItem, FoundItem, ContactMessage, Review, ReviewReply, Claim, Notification
from django.contrib.auth import get_user_model

User = get_user_model()

# Lost Item Serializer
class LostItemSerializer(serializers.ModelSerializer):
    photo_url   = serializers.SerializerMethodField()
    reported_by = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model  = LostItem
        fields = '__all__'
        read_only_fields = ['user', 'submitted_at', 'status']

    def get_photo_url(self, obj):
        if obj.photo:
            return f'http://127.0.0.1:8000{obj.photo.url}'
        return None

# Found Item Serializer
class FoundItemSerializer(serializers.ModelSerializer):
    photo_url   = serializers.SerializerMethodField()
    reported_by = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model  = FoundItem
        fields = '__all__'
        read_only_fields = ['user', 'submitted_at', 'status']

    def get_photo_url(self, obj):
        if obj.photo:
            return f'http://127.0.0.1:8000{obj.photo.url}'
        return None

# Contact Message Serializer
class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = '__all__'


# Review Reply Serializer
class ReviewReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewReply
        fields = '__all__'
        
# Review Serializer
class ReviewSerializer(serializers.ModelSerializer):
    username    = serializers.ReadOnlyField(source='user.username')
    total_likes = serializers.SerializerMethodField()
    reply       = ReviewReplySerializer(read_only=True)

    class Meta:
        model  = Review
        fields = '__all__'

    def get_total_likes(self, obj):
        return obj.total_likes()

# Claim Serializer
class ClaimSerializer(serializers.ModelSerializer):
    claimer_username = serializers.ReadOnlyField(source='claimer.username')
    item_name = serializers.SerializerMethodField()
    item_type = serializers.SerializerMethodField()

    class Meta:
        model = Claim
        fields = [
            'id', 'claimer', 'claimer_username',
            'lost_item', 'found_item',
            'item_name', 'item_type',
            'details', 'status', 'created_at',
        ]
        read_only_fields = ['claimer', 'status', 'created_at']

    def get_item_name(self, obj):
        item = obj.lost_item or obj.found_item
        return item.item_name if item else None

    def get_item_type(self, obj):
        if obj.lost_item:
            return 'lost'
        if obj.found_item:
            return 'found'
        return None

    def validate(self, data):
        lost  = data.get('lost_item')
        found = data.get('found_item')
        if not lost and not found:
            raise serializers.ValidationError(
                "A claim must reference either a lost_item or a found_item."
            )
        if lost and found:
            raise serializers.ValidationError(
                "A claim cannot reference both a lost_item and a found_item."
            )
        return data

# Auth Serializer
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'student_id', 'phone']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        if not value.endswith('@uom.ac.mu'):
            raise serializers.ValidationError("Only UoM email addresses are allowed.")
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

# Notification Serializer
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Notification
        fields = ['id', 'title', 'body', 'is_read', 'created_at', 'item_type', 'item_id']