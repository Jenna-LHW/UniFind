from .models import Notification
 
 
def notification_context(request):
    if not request.user.is_authenticated:
        return {}
 
    unread_qs = Notification.objects.filter(
        recipient=request.user, is_read=False
    )
    recent = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')[:6]
 
    return {
        'unread_notif_count':  unread_qs.count(),
        'recent_notifications': recent,
    }