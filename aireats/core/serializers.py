# core/serializers.py
from rest_framework import serializers
from .models import User, Name

class NameSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)

class UserSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    name = NameSerializer()
    email = serializers.EmailField()
    phone = serializers.CharField()
    role = serializers.IntegerField()
    sex = serializers.CharField(required=False)
    dob = serializers.DateField(required=False)
    nationality = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
