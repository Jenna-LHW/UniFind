from rest_framework import serializers
from .models import LostItem, FoundItem, ContactMessage, Review, ReviewReply
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

# Lost Item Serializer
class LostItemSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()

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
    photo_url = serializers.SerializerMethodField()

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

# Review Serializer
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

# Review Reply Serializer
class ReviewReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewReply
        fields = '__all__'

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