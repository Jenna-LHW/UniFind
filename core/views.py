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
from .models import User, Claim
from django.shortcuts import get_object_or_404
from .models import Notification

# Template views

def home_view(request):
    recent_lost  = LostItem.objects.filter(status__in=['pending', 'found'])[:9]
    recent_found = FoundItem.objects.filter(status__in=['pending', 'claimed'])[:9]

    from itertools import chain
    from operator import attrgetter
    recent_items = sorted(
        chain(recent_lost, recent_found),
        key=attrgetter('submitted_at'),
        reverse=True
    )[:9]

    total_users   = User.objects.count()
    total_items   = LostItem.objects.count() + FoundItem.objects.count()
    total_reunited = (
        LostItem.objects.filter(status='resolved').count() +
        FoundItem.objects.filter(status='resolved').count()
    )

    return render(request, 'core/home.html', {
        'recent_items':   recent_items,
        'total_users':    total_users,
        'total_items':    total_items,
        'total_reunited': total_reunited,
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
    lost_items  = request.user.lost_items.all()
    found_items = request.user.found_items.all()
    claims      = request.user.claims.select_related('lost_item', 'found_item').all()
    return render(request, 'core/profile.html', {
        'user':        request.user,
        'lost_items':  lost_items,
        'found_items': found_items,
        'claims':      claims,
    })

@login_required(login_url='login')
def edit_profile_view(request):
    form = EditProfileForm(request.POST or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('profile')
    return render(request, 'core/edit_profile.html', {'form': form})

def about(request):
    return render(request, 'core/about.html')

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
            name    = form.cleaned_data['name'],
            email   = form.cleaned_data['email'],
            subject = form.cleaned_data['subject'],
            message = form.cleaned_data['message'],
            user    = request.user if request.user.is_authenticated else None,
        )
        messages.success(request, "Your message has been sent! We'll get back to you soon.")
        return redirect('contact')

    return render(request, 'core/contact.html', {'form': form})

@login_required(login_url='login')
def report_lost_view(request):
    form = LostItemForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        lost_item = form.save(commit=False)
        lost_item.user = request.user
        lost_item.save()
        messages.success(request, "Your lost item report has been submitted successfully.")
        return redirect('report_lost')
    return render(request, 'core/report_lost.html', {'form': form, 'user': request.user})

def lost_item_detail_view(request, pk):
    item = get_object_or_404(LostItem, pk=pk)
    return render(request, 'core/lost_item_detail.html', {'item': item})

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
    items    = LostItem.objects.filter(status__in=['pending', 'resolved', 'found'])
    keyword  = request.GET.get('q', '')
    category = request.GET.get('category', '')
    date     = request.GET.get('date', '')
    status   = request.GET.get('status', '')

    if keyword:
        items = items.filter(item_name__icontains=keyword) | items.filter(description__icontains=keyword)
    if category:
        items = items.filter(category=category)
    if date:
        parsed = parse_date(date)
        if parsed:
            items = items.filter(date_lost=parsed)
    if status:
        items = items.filter(status=status)

    return render(request, 'core/browse_lost.html', {
        'items':             items,
        'keyword':           keyword,
        'selected_category': category,
        'selected_date':     date,
        'selected_status':   status,
        'categories':        LostItem.Category.choices,
        'statuses':          LostItem.Status.choices,
    })

def browse_found_view(request):
    items    = FoundItem.objects.filter(status__in=['pending', 'resolved', 'claimed'])
    keyword  = request.GET.get('q', '')
    category = request.GET.get('category', '')
    date     = request.GET.get('date', '')
    status   = request.GET.get('status', '')

    if keyword:
        items = items.filter(item_name__icontains=keyword) | items.filter(description__icontains=keyword)
    if category:
        items = items.filter(category=category)
    if date:
        parsed = parse_date(date)
        if parsed:
            items = items.filter(date_found=parsed)
    if status:
        items = items.filter(status=status)

    return render(request, 'core/browse_found.html', {
        'items':             items,
        'keyword':           keyword,
        'selected_category': category,
        'selected_date':     date,
        'selected_status':   status,
        'categories':        FoundItem.Category.choices,
        'statuses':          FoundItem.Status.choices,
    })

def found_item_detail_view(request, pk):
    item = get_object_or_404(FoundItem, pk=pk)
    return render(request, 'core/found_item_detail.html', {'item': item})

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

    all_reviews   = Review.objects.filter(is_banned=False)
    total         = all_reviews.count()
    avg_rating    = round(sum(r.rating for r in all_reviews) / total, 1) if total else 0
    rating_counts = {i: all_reviews.filter(rating=i).count() for i in range(1, 6)}

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
        r        = form.save(commit=False)
        r.review = review
        r.admin  = request.user
        r.save()
        messages.success(request, "Reply saved successfully.")
        return redirect('review')

    return render(request, 'core/admin_reply.html', {'form': form, 'review': review})

@login_required(login_url='login')
def ban_review_view(request, review_id):
    if not request.user.is_superuser and request.user.role != 'admin':
        return redirect('review')

    review = Review.objects.get(id=review_id)
    if request.method == 'POST':
        ban_reason        = request.POST.get('ban_reason', '')
        review.is_banned  = not review.is_banned
        review.ban_reason = ban_reason if review.is_banned else ''
        review.save()
        msg = "Review banned." if review.is_banned else "Review unbanned."
        messages.success(request, msg)
        return redirect('review')

@login_required
def submit_claim_view(request, item_type, pk):
    # Fetch the specific item clicked based on its ID (pk)
    if item_type == 'lost':
        item = get_object_or_404(LostItem, pk=pk)
    elif item_type == 'found':
        item = get_object_or_404(FoundItem, pk=pk)
    else:
        return redirect('home')

    if request.method == 'POST':
        details = request.POST.get('details')
        # Ensure the claim links to the CORRECT item type
        Claim.objects.create(
            claimer=request.user,
            details=details,
            lost_item=item if item_type == 'lost' else None,
            found_item=item if item_type == 'found' else None
        )
        messages.success(request, "Claim submitted!")
        return redirect('home')

    # Pass 'item' to the template so it displays the correct name
    return render(request, 'core/submit_claim.html', {'item': item})

@login_required(login_url='login')
def notifications_view(request):
    notifications = Notification.objects.filter(recipient=request.user)
    return render(request, 'core/notifications.html', {
        'notifications': notifications,
    })
 
 
# ── AJAX: mark a single notification as read ────────────────────────────────
@login_required(login_url='login')
def notification_mark_read_view(request, pk):
    """POST /notifications/<pk>/mark-read/  →  {ok: true}"""
    if request.method == 'POST':
        Notification.objects.filter(
            pk=pk, recipient=request.user
        ).update(is_read=True)
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False}, status=405)
 
 
# ── AJAX / form POST: mark ALL notifications as read ────────────────────────
@login_required(login_url='login')
def notifications_mark_all_read_view(request):
    """POST /notifications/mark-all-read/  →  {ok: true}"""
    if request.method == 'POST':
        Notification.objects.filter(
            recipient=request.user, is_read=False
        ).update(is_read=True)
        # Support both AJAX (fetch) and plain form POST
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' \
                or 'application/json' in request.headers.get('Content-Type', '') \
                or request.headers.get('Accept', '').startswith('application/json'):
            return JsonResponse({'ok': True})
        # Plain form POST fallback (from the notifications page button)
        return redirect('notifications')
    return JsonResponse({'ok': False}, status=405)

# API views

from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import (
    LostItemSerializer, FoundItemSerializer,
    ContactMessageSerializer, ReviewSerializer,
    ReviewReplySerializer, RegisterSerializer,
    ClaimSerializer,
)
from .models import Notification
from .serializers import NotificationSerializer

User = get_user_model()

class LostItemViewSet(viewsets.ModelViewSet):
    """
    list:   GET  /api/lost-items/
    create: POST /api/lost-items/
    retrieve: GET  /api/lost-items/<pk>/
    update: PUT  /api/lost-items/<pk>/
    partial_update: PATCH /api/lost-items/<pk>/
    destroy: DELETE /api/lost-items/<pk>/
    Filter to current user's items:
        GET /api/lost-items/?mine=true
    """
    queryset = LostItem.objects.all()
    serializer_class = LostItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        # ?mine=true  →  only the authenticated user's items
        if self.request.query_params.get('mine') == 'true':
            qs = qs.filter(user=self.request.user)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class FoundItemViewSet(viewsets.ModelViewSet):
    """
    list:   GET  /api/found-items/
    create: POST /api/found-items/
    retrieve: GET  /api/found-items/<pk>/
    update: PUT  /api/found-items/<pk>/
    partial_update: PATCH /api/found-items/<pk>/
    destroy: DELETE /api/found-items/<pk>/
    Filter to current user's items:
        GET /api/found-items/?mine=true
    """
    queryset = FoundItem.objects.all()
    serializer_class = FoundItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('mine') == 'true':
            qs = qs.filter(user=self.request.user)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ClaimViewSet(viewsets.ModelViewSet):
    """
    list:   GET  /api/claims/              — own claims (admin sees all)
    create: POST /api/claims/              — submit a new claim
    retrieve: GET  /api/claims/<pk>/       — claim detail
    update: PUT/PATCH /api/claims/<pk>/    — admin only (e.g. change status)
    destroy: DELETE /api/claims/<pk>/      — admin only

    Convenience nested routes (read-only):
      GET /api/lost-items/<pk>/claims/
      GET /api/found-items/<pk>/claims/
    """
    serializer_class   = ClaimSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Admins/superusers see every claim; regular users see only their own
        if user.is_superuser or getattr(user, 'role', '') == 'admin':
            return Claim.objects.select_related(
                'claimer', 'lost_item', 'found_item'
            ).all()
        return Claim.objects.select_related(
            'claimer', 'lost_item', 'found_item'
        ).filter(claimer=user)

    def perform_create(self, serializer):
        serializer.save(claimer=self.request.user)

    def update(self, request, *args, **kwargs):
        """Only admins may update a claim (e.g. approve / reject)."""
        user = request.user
        if not (user.is_superuser or getattr(user, 'role', '') == 'admin'):
            return Response(
                {'detail': 'Only admins can update claims.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Only admins may delete a claim."""
        user = request.user
        if not (user.is_superuser or getattr(user, 'role', '') == 'admin'):
            return Response(
                {'detail': 'Only admins can delete claims.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)


class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset           = ContactMessage.objects.all()
    serializer_class   = ContactMessageSerializer
    permission_classes = [AllowAny]


class ReviewViewSet(viewsets.ModelViewSet):
    queryset           = Review.objects.filter(is_banned=False)
    serializer_class   = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], url_path='like')
    def like(self, request, pk=None):
        review = self.get_object()
        like, created = ReviewLike.objects.get_or_create(user=request.user, review=review)
        if not created:
            like.delete()
            liked = False
        else:
            liked = True
        return Response({'liked': liked, 'total_likes': review.total_likes()})


class ReviewReplyViewSet(viewsets.ModelViewSet):
    queryset         = ReviewReply.objects.all()
    serializer_class = ReviewReplySerializer


class RegisterView(generics.CreateAPIView):
    queryset           = User.objects.all()
    serializer_class   = RegisterSerializer
    permission_classes = [AllowAny]


class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "id":          request.user.id,
            "username":    request.user.username,
            "email":       request.user.email,
            "first_name":  request.user.first_name,
            "last_name":   request.user.last_name,
            "role":        request.user.role,
            "phone":       request.user.phone,
            "student_id":  request.user.student_id,
            "date_joined": request.user.date_joined,
        })

    def patch(self, request):
        user = request.user
        allowed_fields = ['first_name', 'last_name', 'email', 'phone', 'student_id']
        for field in allowed_fields:
            if field in request.data:
                setattr(user, field, request.data[field])
        # Handle password change separately
        if 'password' in request.data and request.data['password']:
            user.set_password(request.data['password'])
        user.save()
        return Response({
            "id":          user.id,
            "username":    user.username,
            "email":       user.email,
            "first_name":  user.first_name,
            "last_name":   user.last_name,
            "role":        user.role,
            "phone":       user.phone,
            "student_id":  user.student_id,
            "date_joined": user.date_joined,
        })

class NotificationViewSet(viewsets.ModelViewSet):
    """
    list:           GET   /api/notifications/          — own unread + recent
    retrieve:       GET   /api/notifications/<pk>/
    partial_update: PATCH /api/notifications/<pk>/     — mark as read
    """
    serializer_class   = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    @action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request):
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response({'status': 'ok'})