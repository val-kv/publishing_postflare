from rest_framework import serializers
from .models import Post, User


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone_number', 'password']

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
