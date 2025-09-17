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


# core/views.py 
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


from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from mongoengine.queryset.visitor import Q
import uuid

from .models import User, Menu, Booking, OrderItem, BoardingDetails


# ------------------------
# Restaurant page (menu of a restaurant)
# ------------------------
def restaurant_page(request, username, restaurant_id):
    # Fetch menu
    dishes = Menu.objects(restaurant_id=restaurant_id)

    # Fetch booking
    booking = get_pending_booking(username)
    cart = booking.order if booking else []

    if request.method == "POST":
        action = request.POST.get("action")
        dish_id = request.POST.get("dish_id")

        if not booking:
            return render(request, "core/restaurant.html", {
                "username": username, "restaurant_id": restaurant_id,
                "dishes": dishes, "cart": [], "error": "No active booking"
            })

        menu_item = Menu.objects(dish_id=dish_id).first()
        if not menu_item:
            return render(request, "core/restaurant.html", {
                "username": username, "restaurant_id": restaurant_id,
                "dishes": dishes, "cart": cart, "error": "Invalid dish"
            })

        found = None
        for oi in booking.order:
            if oi.dish_id == dish_id:
                found = oi
                break

        if action == "add":
            if found:
                found.quantity += 1
            else:
                booking.order.append(OrderItem(
                    dish_id=menu_item.dish_id,
                    dish_name=menu_item.dish_name,
                    dish_price=menu_item.price,
                    quantity=1
                ))
        elif action == "remove":
            if found:
                found.quantity -= 1
                if found.quantity <= 0:
                    booking.order = [x for x in booking.order if x.dish_id != dish_id]

        # Recalculate amount
        total_amt = Decimal("0.00")
        for oi in booking.order:
            total_amt += (oi.dish_price * oi.quantity)
        booking.amount = total_amt
        booking.date_time = timezone.now()
        booking.save()

        return redirect(reverse("restaurant_page", kwargs={
            "username": username, "restaurant_id": restaurant_id
        }))

    return render(request, "core/restaurant.html", {
        "username": username,
        "restaurant_id": restaurant_id,
        "dishes": dishes,
        "cart": cart
    })



def get_pending_booking(username):
    booking = Booking.objects(username=username, status="Pending").order_by('-date_time').first()
    if not booking:
        booking = Booking(
            booking_id=str(uuid.uuid4()),
            username=username,
            status="Pending",
            date_time=timezone.now(),
            location="",
            order=[],
            amount=Decimal("0.00")
        )
        booking.save()
    return booking


def booking_page(request, username):
    # Fetch unique restaurants
    restaurants_cursor = Menu.objects.only("restaurant_id", "restaurant_name")
    seen = set()
    restaurants = []
    for m in restaurants_cursor:
        key = (m.restaurant_id, m.restaurant_name)
        if key not in seen:
            seen.add(key)
            restaurants.append({
                "restaurant_id": m.restaurant_id,
                "restaurant_name": m.restaurant_name
            })

    booking = get_pending_booking(username)
    cart = booking.order if booking else []
    total = str(booking.amount) if booking else "0.00"

    if request.method == "POST":
        action = request.POST.get("action")
        dish_id = request.POST.get("dish_id")

        if not booking:
            return render(request, "core/booking.html", {
                "username": username, "restaurants": restaurants,
                "cart": [], "total": "0.00", "error": "No active booking found"
            })

        # Cart operations
        if action in ("add", "remove") and dish_id:
            menu_item = Menu.objects(dish_id=dish_id).first()
            if not menu_item:
                return render(request, "core/booking.html", {
                    "username": username, "restaurants": restaurants,
                    "cart": cart, "total": total, "error": "Invalid dish"
                })

            found = None
            for oi in booking.order:
                if oi.dish_id == dish_id:
                    found = oi
                    break

            if action == "add":
                if found:
                    found.quantity += 1
                else:
                    booking.order.append(OrderItem(
                        dish_id=menu_item.dish_id,
                        dish_name=menu_item.dish_name,
                        dish_price=menu_item.price,
                        quantity=1
                    ))
            elif action == "remove":
                if found:
                    found.quantity -= 1
                    if found.quantity <= 0:
                        booking.order = [x for x in booking.order if x.dish_id != dish_id]

            # Update amount
            total_amt = Decimal("0.00")
            for oi in booking.order:
                total_amt += (oi.dish_price * oi.quantity)
            booking.amount = total_amt
            booking.date_time = timezone.now()
            booking.save()

            return redirect(reverse("booking_page", kwargs={"username": username}))

        # Fetch boarding details but keep status Pending
        elif action == "fetch_details":
            boarding_pass_number = request.POST.get("boarding_pass_number").strip()
            bd = BoardingDetails.objects(boarding_pass_number=boarding_pass_number).first()

            if not bd:
                return render(request, "core/booking.html", {
                    "username": username, "restaurants": restaurants,
                    "cart": cart, "total": total,
                    "error": "Invalid boarding pass number"
                })

            if not booking.order:
                return render(request, "core/booking.html", {
                    "username": username, "restaurants": restaurants,
                    "cart": cart, "total": total,
                    "error": "Cart is empty"
                })

            booking.boarding_pass_number = boarding_pass_number
            booking.location = f"Gate {bd.gate_no} - {bd.departure}"
            booking.status = "Pending"   # keep pending
            booking.date_time = timezone.now()
            booking.save()

            return redirect(reverse("booking_page", kwargs={"username": username}))

        # Place order (actual confirm, you will define later)
        elif action == "place_order":
            if not booking.boarding_pass_number:
                return render(request, "core/booking.html", {
                    "username": username, "restaurants": restaurants,
                    "cart": cart, "total": total,
                    "error": "Fetch boarding details first"
                })

            # For now just show success (later you will add payment etc.)
            return render(request, "core/booking.html", {
                "username": username, "restaurants": restaurants,
                "cart": booking.order, "total": str(booking.amount),
                "booking": booking,
                "msg": "Ready to confirm order (next step)!"
            })
        elif action == "reset_boarding":
            booking.boarding_pass_number = None
            booking.location = ""
            booking.save()
            return redirect(reverse("booking_page", kwargs={"username": username}))


    return render(request, "core/booking.html", {
        "username": username,
        "restaurants": restaurants,
        "cart": cart,
        "total": total,
        "booking": booking
    })

import uuid
from datetime import datetime
from decimal import Decimal
from django.utils import timezone
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import Booking, Payment, Menu, BoardingDetails, OrderItem

# ------------------------------
# Payment page
# ------------------------------
def payment_page(request, username, booking_id):
    booking = Booking.objects(booking_id=booking_id, username=username).first()
    if not booking:
        return render(request, "core/payment.html", {"error": "Booking not found"})

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")
        if not payment_method:
            return render(request, "core/payment.html", {"booking": booking, "error": "Select a payment method"})

        # Generate transaction ID
        transaction_id = f"{username}_{int(datetime.now().timestamp())}"

        # Save payment record
        payment = Payment(
            transaction_id=transaction_id,
            booking_id=booking.booking_id,
            timestamp=timezone.now(),
            payment_method=payment_method
        )
        payment.save()

        # Mock confirm booking
        booking.status = "Confirmed"
        booking.save()

        return redirect(reverse("orders_page", kwargs={"username": username}))

    return render(request, "core/payment.html", {"booking": booking})


# ------------------------------
# Orders page
# ------------------------------
# core/views.py

def orders_page(request, username):
    confirmed_orders = Booking.objects(username=username, status="Confirmed")

    # Collect payment details for each booking
    payments_map = {}
    for booking in confirmed_orders:
        payment = Payment.objects(booking_id=booking.booking_id).first()
        if payment:
            payments_map[booking.booking_id] = payment

    if request.method == "POST":
        booking_id = request.POST.get("booking_id")
        booking = Booking.objects(booking_id=booking_id, username=username).first()
        if booking:
            booking.status = "Completed"
            booking.save()
        return redirect(reverse("orders_page", kwargs={"username": username}))

    return render(
        request,
        "core/orders.html",
        {"orders": confirmed_orders, "payments": payments_map, "username": username},
    )

def order_history_page(request, username):
    # Fetch all completed orders for this user
    completed_orders = Booking.objects(username=username, status="Completed").order_by('-date_time')
    
    return render(request, "core/orderhistory.html", {
        "username": username,
        "orders": completed_orders
    })



