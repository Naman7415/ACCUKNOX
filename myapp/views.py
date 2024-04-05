from django.contrib.auth import authenticate, login
from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Friendship
from .serializers import *
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.throttling import UserRateThrottle
from rest_framework import filters




class SignupView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoginView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email'].lower()
            password = serializer.validated_data['password']
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                return Response("successfully-login",status=status.HTTP_200_OK)
            return Response({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class UserSearchAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['=email','name__icontains']



class FriendRequestThrottle(UserRateThrottle):
    scope = 'friend_request'  

class FriendRequestListCreateAPIView(generics.ListCreateAPIView):
    queryset = Friendship.objects.all()
    serializer_class = FriendshipSerializer
    throttle_classes = [FriendRequestThrottle]

    def create(self, request, *args, **kwargs):
        # Add the from_user to the request data
        request.data['from_user'] = request.user.id
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        to_user = serializer.validated_data['to_user']
        
        if to_user == request.user:
            return Response({"error": "You cannot send a friend request to yourself."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Check if a friend request already exists
        if Friendship.objects.filter(from_user=request.user, to_user=to_user).exists():
            return Response({"detail": "You've already sent a friend request to this user."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        # Save the from_user based on the request user
        serializer.save(from_user=self.request.user)




class FriendListAPIView(generics.ListAPIView):
    serializer_class = FriendshipSerializer
    def get_queryset(self):
        return Friendship.objects.filter(
            Q(from_user=self.request.user, accepted=True) |
            Q(to_user=self.request.user, accepted=True)
        )


class PendingFriendRequestListAPIView(generics.ListAPIView):
    serializer_class = FriendshipSerializer1
    def get_queryset(self):
        return Friendship.objects.filter(to_user=self.request.user, accepted=False)



class RejectFriendRequestAPIView(generics.DestroyAPIView):
    queryset = Friendship.objects.all()
    serializer_class = FriendshipSerializer
    
    def delete(self, request, *args, **kwargs):
        friendship = get_object_or_404(Friendship, from_user=request.user, to_user=self.kwargs['pk'])
        friendship.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
        
        
    
class AcceptFriendRequestView(APIView):
    def post(self, request, request_id):
        friend_request = get_object_or_404(Friendship, id=request_id, to_user=request.user, accepted=False)
        serializer = FriendRequestAcceptSerializer(friend_request, data={'accepted': True})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
