from django.urls import path
from . import views
from core.views import (
    notifications_view,
    notification_mark_read_view,
    notifications_mark_all_read_view,
)

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),

    path('report/lost/',  views.report_lost_view,  name='report_lost'),
    path('report/found/', views.report_found_view, name='report_found'),

    path('browse/lost/', views.browse_lost_view, name='browse_lost'),
    path('browse/found/', views.browse_found_view, name='browse_found'),

    path('browse/found/<int:pk>/', views.found_item_detail_view, name='found_item_detail'),
    path('browse/lost/<int:pk>/', views.lost_item_detail_view, name='lost_item_detail'),

    path('claim/<str:item_type>/<int:pk>/', views.submit_claim_view, name='submit_claim'),

    path('review/', views.review_view, name='review'),
    path('review/<int:review_id>/like/', views.like_review_view, name='like_review'),
    path('review/<int:review_id>/reply/', views.admin_reply_view, name='admin_reply'),
    path('review/<int:review_id>/ban/', views.ban_review_view, name='ban_review'),
    
    path('about/', views.about, name='about'),

    path('contact/', views.contact_view, name='contact'),

    path('notifications/', notifications_view, name='notifications'),
    path('notifications/mark-all-read/', notifications_mark_all_read_view, name='notifications_mark_all_read'),
    path('notifications/<int:pk>/mark-read/', notification_mark_read_view, name='notification_mark_read'),
]
