from django.shortcuts import render

# Create your views here.
# core/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import User

@api_view(["POST"])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"error": "Username and password required"}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects(username=username).first()
    if user and user.password == password:  # TODO: hash later
        return Response({
            "message": "Login successful",
            "username": user.username,
            "role": user.role
        }, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
