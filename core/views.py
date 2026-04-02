from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, EditProfileForm, ContactForm, LostItemForm, FoundItemForm
from .models import ContactMessage, LostItem, FoundItem
from django.utils.dateparse import parse_date
from .models import Review, ReviewReply, ReviewLike
from .forms  import ReviewForm, AdminReplyForm
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .models import User

def home_view(request):
    recent_lost  = LostItem.objects.filter(status__in=['pending', 'active'])[:3]
    recent_found = FoundItem.objects.filter(status__in=['pending', 'active'])[:3]

    # Combine and sort by submitted_at, take latest 3
    from itertools import chain
    from operator import attrgetter
    recent_items = sorted(
        chain(recent_lost, recent_found),
        key=attrgetter('submitted_at'),
        reverse=True
    )[:3]

    total_users = User.objects.count()
    total_items = LostItem.objects.count() +  FoundItem.objects.count()

    return render(request, 'core/home.html', {
        'recent_items': recent_items,
        'total_users':  total_users,
        'total_items': total_items,
    })

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

def browse_found_view(request):
    items = FoundItem.objects.filter(status__in=['pending', 'active'])
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
            items = items.filter(date_found=parsed)

    return render(request, 'core/browse_found.html', {
        'items': items,
        'keyword': keyword,
        'selected_category': category,
        'selected_date': date,
        'categories': FoundItem.Category.choices,
    })

def review_view(request):
    reviews     = Review.objects.filter(is_banned=False).select_related('user', 'reply')
    user_review = None
    form        = None

    if request.user.is_authenticated:
        user_review = Review.objects.filter(user=request.user).first()
        form        = ReviewForm(request.POST or None)

        if request.method == 'POST' and form.is_valid():
            if user_review:
                messages.error(request, "You have already submitted a review.")
            else:
                review      = form.save(commit=False)
                review.user = request.user
                review.save()
                messages.success(request, "Your review has been submitted!")
            return redirect('review')

    # Rating summary
    all_reviews  = Review.objects.filter(is_banned=False)
    total        = all_reviews.count()
    avg_rating   = round(sum(r.rating for r in all_reviews) / total, 1) if total else 0
    rating_counts = {i: all_reviews.filter(rating=i).count() for i in range(1, 6)}

    # Liked reviews by current user
    liked_ids = []
    if request.user.is_authenticated:
        liked_ids = list(ReviewLike.objects.filter(
            user=request.user
        ).values_list('review_id', flat=True))

    banned_reviews = Review.objects.filter(is_banned=True) if (
        request.user.is_authenticated and (
            request.user.is_superuser or request.user.role == 'admin'
        )
    ) else []

    return render(request, 'core/review.html', {
        'reviews':        reviews,
        'banned_reviews': banned_reviews,
        'form':           form,
        'user_review':    user_review,
        'avg_rating':     avg_rating,
        'total':          total,
        'rating_counts':  rating_counts,
        'liked_ids':      liked_ids,
    })

@login_required(login_url='login')
def like_review_view(request, review_id):
    if request.method == 'POST':
        review = Review.objects.get(id=review_id)
        like, created = ReviewLike.objects.get_or_create(user=request.user, review=review)
        if not created:
            like.delete()
            liked = False
        else:
            liked = True
        return JsonResponse({'liked': liked, 'total_likes': review.total_likes()})


@login_required(login_url='login')
def admin_reply_view(request, review_id):
    if not request.user.is_superuser and request.user.role != 'admin':
        return redirect('review')

    review = Review.objects.get(id=review_id)
    reply  = getattr(review, 'reply', None)
    form   = AdminReplyForm(request.POST or None, instance=reply)

    if request.method == 'POST' and form.is_valid():
        r         = form.save(commit=False)
        r.review  = review
        r.admin   = request.user
        r.save()
        messages.success(request, "Reply saved successfully.")
        return redirect('review')

    return render(request, 'core/admin_reply.html', {
        'form':   form,
        'review': review,
    })


@login_required(login_url='login')
def ban_review_view(request, review_id):
    if not request.user.is_superuser and request.user.role != 'admin':
        return redirect('review')

    review = Review.objects.get(id=review_id)

    if request.method == 'POST':
        ban_reason      = request.POST.get('ban_reason', '')
        review.is_banned = not review.is_banned
        review.ban_reason = ban_reason if not review.is_banned else ''
        review.save()
        msg = "Review banned." if review.is_banned else "Review unbanned."
        messages.success(request, msg)
        return redirect('review')

# API views
from rest_framework import viewsets, generics
from django.contrib.auth import get_user_model
from .models import LostItem, FoundItem, ContactMessage, Review, ReviewReply
from .serializers import (
    LostItemSerializer, FoundItemSerializer,
    ContactMessageSerializer, ReviewSerializer, ReviewReplySerializer, RegisterSerializer
)
from rest_framework.permissions import AllowAny, IsAuthenticated

User = get_user_model()

# Lost Items API
class LostItemViewSet(viewsets.ModelViewSet):
    queryset = LostItem.objects.all()
    serializer_class = LostItemSerializer

# Found Items API
class FoundItemViewSet(viewsets.ModelViewSet):
    queryset = FoundItem.objects.all()
    serializer_class = FoundItemSerializer

# Contact Messages API
class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer

# Reviews API
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

# Review Replies API
class ReviewReplyViewSet(viewsets.ModelViewSet):
    queryset = ReviewReply.objects.all()
    serializer_class = ReviewReplySerializer

# Register
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

# Get current user
from rest_framework.views import APIView
from rest_framework.response import Response

class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "username": request.user.username,
            "email": request.user.email
        })