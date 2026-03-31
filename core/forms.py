from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role  = forms.ChoiceField(choices=[
        (User.Role.STUDENT, 'Student'),
        (User.Role.STAFF,   'Staff'),
    ])

    class Meta:
        model  = User
        fields = ['username', 'email', 'role', 'student_id', 'phone', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith('@umail.uom.ac.mu'):
            raise forms.ValidationError("Only UoM email addresses (@umail.uom.ac.mu) are allowed.")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        student_id = cleaned_data.get('student_id')
        if role == User.Role.STUDENT and not student_id:
            self.add_error('student_id', 'Student ID is required for students.')
        return cleaned_data