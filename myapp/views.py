from django.contrib.auth import authenticate, login
from rest_framework import permissions, status, views
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




class SignupView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoginView(views.APIView):
    permission_classes = [permissions.AllowAny]

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




User = get_user_model()

class UserSearchAPIView(generics.ListAPIView):
    serializer_class = UserLoginSerializer
    pagination_class = PageNumberPagination
    permission_classes = [permissions.IsAuthenticated]
    page_size = 10

    def get(self,request,pk=None):
        name = self.request.query_params.get('email', None)
        if name is not None:
            queryset = User.objects.filter(email__istartswith=name)
            serilaizer = UserCreateSerializer(queryset,many=True)
            return Response(serilaizer.data,status=status.HTTP_200_OK )
        




class FriendRequestListCreateAPIView(generics.ListCreateAPIView):
    queryset = Friendship.objects.all()
    serializer_class = FriendshipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data['to_user'] == request.user:
            return Response({"error": "You cannot send a friend request to yourself."},
                            status=status.HTTP_400_BAD_REQUEST)
        now = timezone.now()
        minute_ago = now - timedelta(minutes=1)
        request_count = Friendship.objects.filter(
            from_user=request.user,
            created_at__gte=minute_ago
        ).count()

        if request_count >= 3:
            return Response({"error": "You have exceeded the limit of friend requests within a minute."},
                            status=status.HTTP_429_TOO_MANY_REQUESTS)
            
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)




class FriendListAPIView(generics.ListAPIView):
    serializer_class = FriendshipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Friendship.objects.filter(
            Q(from_user=self.request.user, accepted=True) |
            Q(to_user=self.request.user, accepted=True)
        )



class PendingFriendRequestListAPIView(generics.ListAPIView):
    serializer_class = FriendshipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Friendship.objects.filter(to_user=self.request.user, accepted=False)




class RejectFriendRequestAPIView(generics.DestroyAPIView):
    queryset = Friendship.objects.all()
    serializer_class = FriendshipSerializer
    permission_classes = [permissions.IsAuthenticated]

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
