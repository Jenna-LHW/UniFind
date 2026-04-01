from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'student','Student'
        STAFF = 'staff','Staff'
        ADMIN = 'admin','Admin'

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    student_id = models.CharField(max_length=20, blank=True)  # for students
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.subject} — {self.name}"

class LostItem(models.Model):
    class Category(models.TextChoices):
        ELECTRONICS = 'electronics', 'Electronics'
        CLOTHING = 'clothing', 'Clothing'
        ACCESSORIES = 'accessories', 'Accessories'
        BOOKS_STATIONERY = 'books_stationery', 'Books & Stationery'
        ID_CARDS = 'id_cards', 'ID & Cards'
        BAGS = 'bags', 'Bags'
        KEYS = 'keys', 'Keys'
        OTHER = 'other', 'Other'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACTIVE = 'active', 'Active'
        RESOLVED = 'resolved', 'Resolved'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lost_items')
    item_name = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=Category.choices)
    description = models.TextField()
    last_seen = models.CharField(max_length=200)
    photo = models.ImageField(upload_to='lost_items/', blank=True, null=True)
    date_lost = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.item_name} — {self.user.username}"