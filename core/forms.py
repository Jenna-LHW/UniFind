from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, LostItem

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

class EditProfileForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First name'}),
            'last_name':  forms.TextInput(attrs={'placeholder': 'Last name'}),
            'phone':      forms.TextInput(attrs={'placeholder': 'e.g. (+230) 12345678'}),
        }

class ContactForm(forms.Form):
    name    = forms.CharField(max_length=100)
    email   = forms.EmailField()
    subject = forms.CharField(max_length=150)
    message = forms.CharField(widget=forms.Textarea)

class LostItemForm(forms.ModelForm):
    class Meta:
        model  = LostItem
        fields = ['item_name', 'category', 'description', 'last_seen', 'date_lost', 'photo']
        widgets = {
            'item_name': forms.TextInput(attrs={'placeholder': 'e.g. Black HP Laptop'}),
            'description': forms.Textarea(attrs={'placeholder': 'Describe the item in detail — color, brand, size, any identifying marks...', 'rows': 4}),
            'last_seen': forms.TextInput(attrs={'placeholder': 'e.g. Near the library entrance'}),
            'date_lost': forms.DateInput(attrs={'type': 'date'}),
        }