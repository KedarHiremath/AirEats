'''from django.shortcuts import render


# core/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import User
from django.contrib.auth.hashers import check_password  # ✅ to verify hashed password


@api_view(["POST"])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"error": "Username and password required"}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects(username=username).first()
    if not user:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    # ✅ Verify password hash
    if check_password(password, user.password):
        return Response({
            "message": "Login successful",
            "username": user.username,
            "role": user.role
        }, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)



# core/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import User, Name
from mongoengine.errors import NotUniqueError
from django.contrib.auth.hashers import make_password  # ✅ for hashing


@csrf_exempt
def signup(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # -------- Mandatory fields --------
            mandatory_fields = ["username", "password", "first_name", "last_name", "email", "phone", "role"]
            for field in mandatory_fields:
                if field not in data or not data[field]:
                    return JsonResponse({"success": False, "message": f"Missing required field: {field}"}, status=400)


            # -------- Optional fields --------
            sex = data.get("sex") if data.get("sex") in ["Male", "Female", "Other"] else None
            dob = data.get("dob") or None
            nationality = data.get("nationality") or None
            address = data.get("address") or None


            # -------- Create User with hashed password --------
            user = User(
                username=data["username"],
                password=make_password(data["password"]),  # 🔒 store hashed password
                name=Name(
                    first_name=data["first_name"],
                    last_name=data["last_name"]
                ),
                email=data["email"],
                phone=data["phone"],
                role=int(data["role"]),
                sex=sex,
                dob=dob,
                nationality=nationality,
                address=address
            )
            user.save()

            return JsonResponse({"success": True, "message": "User registered successfully"}, status=201)

        except NotUniqueError:
            return JsonResponse({"success": False, "message": "Username, email, or phone already exists"}, status=409)

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
'''
# core/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password, check_password
from mongoengine.errors import NotUniqueError
import json

from .models import User, Name


# ===========================
# Login API (username/email/phone)
# ===========================
from mongoengine.queryset.visitor import Q  # ✅ for OR queries

@api_view(["POST"])
def login(request):
    identifier = request.data.get("identifier")  # can be username/email/phone
    password = request.data.get("password")

    if not identifier or not password:
        return Response({"success": False, "message": "Identifier and password required"},
                        status=status.HTTP_400_BAD_REQUEST)

    # ✅ Search by username OR email OR phone
    user = User.objects(Q(username=identifier) | Q(email=identifier) | Q(phone=identifier)).first()

    if not user:
        return Response({"success": False, "message": "Invalid credentials"},
                        status=status.HTTP_401_UNAUTHORIZED)

    # ✅ Verify hashed password
    if check_password(password, user.password):
        return Response({
            "success": True,
            "message": "Login successful",
            "username": user.username,
            "role": user.role
        }, status=status.HTTP_200_OK)
    else:
        return Response({"success": False, "message": "Invalid credentials"},
                        status=status.HTTP_401_UNAUTHORIZED)



# ===========================
# Signup API
# ===========================
@csrf_exempt
def signup(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # -------- Mandatory fields --------
            mandatory_fields = ["username", "password", "first_name", "last_name", "email", "phone", "role"]
            for field in mandatory_fields:
                if field not in data or not data[field]:
                    return JsonResponse({"success": False, "message": f"Missing required field: {field}"}, status=400)

            # -------- Optional fields --------
            sex = data.get("sex") if data.get("sex") in ["Male", "Female", "Other"] else None
            dob = data.get("dob") or None
            nationality = data.get("nationality") or None
            address = data.get("address") or None

            # -------- Create User with hashed password --------
            user = User(
                username=data["username"],
                password=make_password(data["password"]),  # 🔒 hash password
                name=Name(
                    first_name=data["first_name"],
                    last_name=data["last_name"]
                ),
                email=data["email"],
                phone=data["phone"],
                role=int(data["role"]),
                sex=sex,
                dob=dob,
                nationality=nationality,
                address=address
            )
            user.save()

            return JsonResponse({"success": True, "message": "User registered successfully"}, status=201)

        except NotUniqueError as e:
            # Check which unique field caused the conflict
            if "username" in str(e):
                msg = "Username already exists"
            elif "email" in str(e):
                msg = "Email already exists"
            elif "phone" in str(e):
                msg = "Phone already exists"
            else:
                msg = "Duplicate entry"
            return JsonResponse({"success": False, "message": msg}, status=409)

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

## Home view
from django.shortcuts import render

def home(request):
    return render(request, 'core/home.html')
