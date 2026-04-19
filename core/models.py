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

    def save(self, *args, **kwargs):
        is_new = self._state.adding          # True only on first save
        super().save(*args, **kwargs)

        item = self.lost_item or self.found_item

        if self.lost_item:
            if self.status == 'pending':
                item.status = 'found'
            elif self.status == 'returned':
                item.status = 'resolved'
            elif self.status == 'rejected':
                item.status = 'pending'
        elif self.found_item:
            if self.status == 'pending':
                item.status = 'claimed'
            elif self.status == 'returned':
                item.status = 'resolved'
            elif self.status == 'rejected':
                item.status = 'pending'
        item.save()

        # ── Fire notification to item owner on new claim ──
        if is_new:
            item_type = 'lost' if self.lost_item else 'found'
            Notification.objects.create(
                recipient  = item.user,
                title      = f"New claim on your {item_type} item",
                body       = (
                    f"{self.claimer.username} submitted a claim on "
                    f'"{item.item_name}". Details: {self.details[:80]}'
                ),
                item_type  = item_type,
                item_id    = item.pk,
            )

    def __str__(self):
        item = self.lost_item or self.found_item
        return f"Claim by {self.claimer.username} for {item.item_name}"

class Notification(models.Model):
    class NotifType(models.TextChoices):
        CLAIM = 'claim', 'Claim'
        MATCH = 'match', 'Potential Match'
        OTHER = 'other', 'Other'

    recipient   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title       = models.CharField(max_length=150)
    body        = models.TextField()
    is_read     = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    # optional deep-link info
    item_type         = models.CharField(max_length=10, blank=True)  # 'lost' | 'found'
    item_id           = models.PositiveIntegerField(null=True, blank=True)
    notification_type = models.CharField(
        max_length=10,
        choices=NotifType.choices,
        default=NotifType.OTHER,
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"→ {self.recipient.username}: {self.title}"


#  Potential-match notification helper 
def _location_overlap(loc_a: str, loc_b: str) -> bool:
    STOP = {'at', 'the', 'a', 'in', 'on', 'near', 'by', 'of', 'and', 'or'}
    words_a = {w.lower() for w in loc_a.split() if len(w) > 2 and w.lower() not in STOP}
    words_b = {w.lower() for w in loc_b.split() if len(w) > 2 and w.lower() not in STOP}
    return bool(words_a & words_b)


def fire_match_notifications(new_item, new_item_type: str):
    if new_item_type == 'lost':
        new_location = new_item.last_seen
        candidates   = FoundItem.objects.filter(
            status__in=['pending', 'claimed']
        ).exclude(user=new_item.user)
        candidate_type = 'found'
    else:
        new_location = new_item.found_at
        candidates   = LostItem.objects.filter(
            status__in=['pending', 'found']
        ).exclude(user=new_item.user)
        candidate_type = 'lost'

    new_name_words = {
        w.lower() for w in new_item.item_name.split() if len(w) >= 3
    }

    for old_item in candidates:
        old_location = old_item.found_at if candidate_type == 'found' else old_item.last_seen
        old_name_words = {
            w.lower() for w in old_item.item_name.split() if len(w) >= 3
        }

        # Must share location AND (category OR name word)
        if not _location_overlap(new_location, old_location):
            continue
        category_match = new_item.category == old_item.category
        name_match     = bool(new_name_words & old_name_words)
        if not (category_match or name_match):
            continue

        # Notify the NEW poster about the old item 
        Notification.objects.create(
            recipient         = new_item.user,
            title             = "This item might belong to someone — check it out!",
            body              = (
                f'A "{old_item.item_name}" was reported '
                f'{"found" if candidate_type == "found" else "lost"} '
                f'near "{old_location}". It could match your report.'
            ),
            item_type         = candidate_type,
            item_id           = old_item.pk,
            notification_type = Notification.NotifType.MATCH,
        )

        # Notify the OLD poster about the new item 
        Notification.objects.create(
            recipient         = old_item.user,
            title             = "This item might be yours — check it out!",
            body              = (
                f'Someone just reported '
                f'{"losing" if new_item_type == "lost" else "finding"} '
                f'a "{new_item.item_name}" near "{new_location}". '
                f'It could be related to your post.'
            ),
            item_type         = new_item_type,
            item_id           = new_item.pk,
            notification_type = Notification.NotifType.MATCH,
        )