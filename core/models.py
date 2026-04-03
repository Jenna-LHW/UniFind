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
        FOUND = 'found', 'Found'
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

class FoundItem(models.Model):
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
        PENDING  = 'pending', 'Pending'
        CLAIMED   = 'claimed', 'Claimed'
        RESOLVED = 'resolved', 'Resolved'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='found_items')
    item_name = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=Category.choices)
    description  = models.TextField()
    found_at = models.CharField(max_length=200)
    photo = models.ImageField(upload_to='found_items/', blank=True, null=True)
    date_found = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.item_name} — {self.user.username}"

class Review(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating     = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_banned  = models.BooleanField(default=False)
    ban_reason = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} — {self.rating}★"

    def total_likes(self):
        return self.likes.count()


class ReviewReply(models.Model):
    review     = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='reply')
    admin      = models.ForeignKey(User, on_delete=models.CASCADE)
    comment    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reply to {self.review}"


class ReviewLike(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='likes')
    user   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_likes')

    class Meta:
        unique_together = ('review', 'user')

    def __str__(self):
        return f"{self.user.username} likes review {self.review.id}"

class Claim(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('returned', 'Returned'),
        ('rejected', 'Rejected'),
    ]

    claimer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='claims')
    # Link to either a lost or found item
    lost_item = models.ForeignKey('LostItem', on_delete=models.CASCADE, null=True, blank=True)
    found_item = models.ForeignKey('FoundItem', on_delete=models.CASCADE, null=True, blank=True)
    
    details = models.TextField(help_text="Provide details to verify ownership or discovery.")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        item = self.lost_item or self.found_item
        return f"Claim by {self.claimer.username} for {item.item_name}"