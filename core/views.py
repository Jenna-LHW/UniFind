from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, EditProfileForm, ContactForm, LostItemForm, FoundItemForm
from .models import ContactMessage, LostItem, FoundItem
from django.utils.dateparse import parse_date

def home_view(request):
    return render(request, 'core/home.html', {'user': request.user})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.role = form.cleaned_data['role']
        user.save()
        messages.success(request, "Account created! You can now log in.")
        return redirect('login')

    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'core/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required(login_url='login')
def profile_view(request):
    return render(request, 'core/profile.html', {'user': request.user})

@login_required(login_url='login')
def edit_profile_view(request):
    form = EditProfileForm(request.POST or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('profile')
    return render(request, 'core/edit_profile.html', {'form': form})


def contact_view(request):
    initial_data = {}
    if request.user.is_authenticated:
        initial_data = {
            'name':  request.user.get_full_name() or request.user.username,
            'email': request.user.email,
        }

    form = ContactForm(request.POST or None, initial=initial_data)

    if request.method == 'POST' and form.is_valid():
        ContactMessage.objects.create(
            name = form.cleaned_data['name'],
            email = form.cleaned_data['email'],
            subject = form.cleaned_data['subject'],
            message = form.cleaned_data['message'],
            user = request.user if request.user.is_authenticated else None,
        )
        messages.success(request, "Your message has been sent! We'll get back to you soon.")
        return redirect('contact')

    return render(request, 'core/contact.html', {'form': form})

@login_required(login_url='login')
def report_lost_view(request):
    initial_data = {
        'username': request.user.username,
        'email':    request.user.email,
    }
    form = LostItemForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        lost_item = form.save(commit=False)
        lost_item.user = request.user
        lost_item.save()
        messages.success(request, "Your lost item report has been submitted successfully.")
        return redirect('report_lost')

    return render(request, 'core/report_lost.html', {'form': form, 'user': request.user})

@login_required(login_url='login')
def report_found_view(request):
    form = FoundItemForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        found_item = form.save(commit=False)
        found_item.user = request.user
        found_item.save()
        messages.success(request, "Your found item report has been submitted successfully.")
        return redirect('report_found')

    return render(request, 'core/report_found.html', {'form': form, 'user': request.user})

def browse_lost_view(request):
    items = LostItem.objects.filter(status__in=['pending', 'active'])
    keyword = request.GET.get('q', '')
    category = request.GET.get('category', '')
    date = request.GET.get('date', '')

    if keyword:
        items = items.filter(item_name__icontains=keyword) | items.filter(description__icontains=keyword)

    if category:
        items = items.filter(category=category)

    if date:
        parsed = parse_date(date)
        if parsed:
            items = items.filter(date_lost=parsed)

    return render(request, 'core/browse_lost.html', {
        'items': items,
        'keyword': keyword,
        'selected_category': category,
        'selected_date': date,
        'categories': LostItem.Category.choices,
    })