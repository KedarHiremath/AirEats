# core/views.py
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from mongoengine.errors import NotUniqueError

from .models import User, Name

@csrf_exempt
def signup(request):
    if request.method == "POST":
        data = request.POST

        # Required fields
        username = data.get("username")
        password = data.get("password")
        confirm_password = data.get("confirm_password")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        phone = data.get("phone")

        # Optional fields
        sex = data.get("sex") if data.get("sex") in ["Male", "Female", "Other"] else None
        dob = data.get("dob") or None
        nationality = data.get("nationality") or None
        address = data.get("address") or None

        # Validation
        if not all([username, password, confirm_password, first_name, last_name, email, phone]):
            return render(request, "core/signup.html", {"error": "All required fields must be filled"})

        if password != confirm_password:
            return render(request, "core/signup.html", {"error": "Passwords do not match"})

        try:
            # Create user with default role = 1 (Customer)
            user = User(
                username=username,
                password=make_password(password),
                name=Name(first_name=first_name, last_name=last_name),
                email=email,
                phone=phone,
                role=1,  # default Customer
                sex=sex,
                dob=dob,
                nationality=nationality,
                address=address
            )
            user.save()
            # Redirect to login page after success
            return redirect("login_page")

        except NotUniqueError as e:
            if "username" in str(e):
                msg = "Username already exists"
            elif "email" in str(e):
                msg = "Email already exists"
            elif "phone" in str(e):
                msg = "Phone already exists"
            else:
                msg = "Duplicate entry"
            return render(request, "core/signup.html", {"error": msg})

        except Exception as e:
            return render(request, "core/signup.html", {"error": str(e)})

    # GET request
    return render(request, "core/signup.html")

# core/views.py
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from mongoengine.queryset.visitor import Q
from django.contrib.auth.hashers import check_password

from .models import User

# -----------------------
# Home View
# -----------------------
def home(request):
    return render(request, 'core/home.html')

'''
# -----------------------
# Login View
# -----------------------
@csrf_exempt
def login_view(request):
    if request.method == "POST":
        identifier = request.POST.get("identifier")  # username/email/phone
        password = request.POST.get("password")

        if not identifier or not password:
            return render(request, "core/login.html", {"error": "Both fields are required"})

        # Search by username OR email OR phone
        user = User.objects(Q(username=identifier) | Q(email=identifier) | Q(phone=identifier)).first()

        if not user:
            return render(request, "core/login.html", {"error": "Invalid credentials"})

        if check_password(password, user.password):
            # Successful login → redirect to booking page with username
            return redirect(f"/booking/{user.username}/")
        else:
            return render(request, "core/login.html", {"error": "Invalid credentials"})

    # GET request
    return render(request, "core/login.html")
'''

# core/views.py (add at the bottom)
def booking_page(request, username):
    # You can fetch user-specific booking details here
    return render(request, "core/booking.html", {"username": username})


# core/views.py
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from mongoengine.queryset.visitor import Q
from django.contrib.auth.hashers import check_password
from .models import User
from django.urls import reverse

@csrf_exempt
def login_view(request):
    if request.method == "POST":
        identifier = request.POST.get("identifier")  # username/email/phone
        password = request.POST.get("password")

        if not identifier or not password:
            return render(request, "core/login.html", {"error": "Both fields are required"})

        # Search by username OR email OR phone
        user = User.objects(Q(username=identifier) | Q(email=identifier) | Q(phone=identifier)).first()

        if not user:
            return render(request, "core/login.html", {"error": "Invalid credentials"})

        if check_password(password, user.password):
            # ✅ Use reverse() to generate URL for booking page
            booking_url = reverse('booking_page', kwargs={'username': user.username})
            return redirect(booking_url)
        else:
            return render(request, "core/login.html", {"error": "Invalid credentials"})

    return render(request, "core/login.html")
