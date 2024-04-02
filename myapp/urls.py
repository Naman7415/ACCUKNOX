from django.urls import path
from .views import *
from .import views
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('search/',UserSearchAPIView.as_view(),name='search'),
    path('friend-request/', FriendRequestListCreateAPIView.as_view(), name='friend-request'),
    path('accept-friend-request/<int:request_id>/', AcceptFriendRequestView.as_view(), name='accept-friend-request'),
    path('friends/', FriendListAPIView.as_view(), name='friends'),
    path('pending-requests/', PendingFriendRequestListAPIView.as_view(), name='pending-requests'),
    path('reject-request/<int:pk>/', RejectFriendRequestAPIView.as_view(), name='reject-request'),

]