from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'student','Student'
        STAFF = 'staff','Staff'
        ADMIN = 'admin','Admin'

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.ADMIN)
    student_id = models.CharField(max_length=20, blank=True)  # for students
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

