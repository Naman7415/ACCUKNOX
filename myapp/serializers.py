
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Friendship



User = get_user_model()

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        email = validated_data['email'].lower()
        password = validated_data['password']
        user = User.objects.create_user(email=email, password=password)
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    

class FriendshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = '__all__'

class FriendRequestAcceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = ['accepted']