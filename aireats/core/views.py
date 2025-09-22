# core/views.py
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from mongoengine.errors import NotUniqueError
from mongoengine.queryset.visitor import Q
from decimal import Decimal
import uuid
from datetime import datetime

from .models import User, Name, Menu, Booking, OrderItem, BoardingDetails, Payment

# ------------------------
# Signup
# ------------------------
@csrf_exempt
def signup(request):
    if request.method == "POST":
        data = request.POST
        username = data.get("username")
        password = data.get("password")
        confirm_password = data.get("confirm_password")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        phone = data.get("phone")
        sex = data.get("sex") if data.get("sex") in ["Male", "Female", "Other"] else None
        dob = data.get("dob") or None
        nationality = data.get("nationality") or None
        address = data.get("address") or None

        if not all([username, password, confirm_password, first_name, last_name, email, phone]):
            return render(request, "core/signup.html", {"error": "All required fields must be filled"})

        if password != confirm_password:
            return render(request, "core/signup.html", {"error": "Passwords do not match"})

        try:
            user = User(
                username=username,
                password=make_password(password),
                name=Name(first_name=first_name, last_name=last_name),
                email=email,
                phone=phone,
                role=1,
                sex=sex,
                dob=dob,
                nationality=nationality,
                address=address
            )
            user.save()
            return redirect("login_page")
        except NotUniqueError as e:
            msg = "Duplicate entry"
            if "username" in str(e): msg = "Username already exists"
            elif "email" in str(e): msg = "Email already exists"
            elif "phone" in str(e): msg = "Phone already exists"
            return render(request, "core/signup.html", {"error": msg})
        except Exception as e:
            return render(request, "core/signup.html", {"error": str(e)})

    return render(request, "core/signup.html")


# ------------------------
# Login
# ------------------------
@csrf_exempt
def login_view(request):
    if request.method == "POST":
        identifier = request.POST.get("identifier")
        password = request.POST.get("password")
        if not identifier or not password:
            return render(request, "core/login.html", {"error": "Both fields are required"})
        user = User.objects(Q(username=identifier) | Q(email=identifier) | Q(phone=identifier)).first()
        if not user or not check_password(password, user.password):
            return render(request, "core/login.html", {"error": "Invalid credentials"})
        booking_url = reverse('booking_page', kwargs={'username': user.username})
        return redirect(booking_url)
    return render(request, "core/login.html")


# ------------------------
# Home
# ------------------------
def home(request):
    return render(request, 'core/home.html')


# ------------------------
# Helper: Get or create pending booking
# ------------------------
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


# ------------------------
# Booking page with mock restaurants & cart
# ------------------------
@csrf_exempt
def booking_page(request, username):
    # ------------------
    # MOCK restaurant list (for testing)
    # ------------------
    restaurants = [
        {"restaurant_id": "dominos", "restaurant_name": "Domino's Pizza"},
        {"restaurant_id": "kfc", "restaurant_name": "KFC"},
        {"restaurant_id": "subway", "restaurant_name": "Subway"},
        {"restaurant_id": "starbucks", "restaurant_name": "Starbucks"},
    ]

    booking = get_pending_booking(username)
    cart = booking.order if booking else []
    total = str(booking.amount) if booking else "0.00"

    if request.method == "POST":
        action = request.POST.get("action")
        dish_id = request.POST.get("dish_id")

        # Add / Remove items from cart
        if action in ("add", "remove") and dish_id:
            # Look in MongoDB Menu
            menu_item = Menu.objects(dish_id=dish_id).first()
            # If not found (mock), try from mock restaurant menu
            if not menu_item:
                mock_menus = {
                    "dominos": [
                        {"dish_id": "d1", "dish_name": "Margherita Pizza", "veg": True, "price": Decimal("199")},
                        {"dish_id": "d2", "dish_name": "Veggie Paradise", "veg": True, "price": Decimal("249")},
                        {"dish_id": "d3", "dish_name": "Peppy Paneer", "veg": True, "price": Decimal("299")},
                        {"dish_id": "d4", "dish_name": "Chicken Dominator", "veg": False, "price": Decimal("349")},
                        {"dish_id": "d5", "dish_name": "Garlic Breadsticks", "veg": True, "price": Decimal("129")},
                    ],
                    "kfc": [
                        {"dish_id": "k1", "dish_name": "Zinger Burger", "veg": False, "price": Decimal("199")},
                        {"dish_id": "k2", "dish_name": "Popcorn Chicken", "veg": False, "price": Decimal("249")},
                        {"dish_id": "k3", "dish_name": "Veg Zinger", "veg": True, "price": Decimal("179")},
                        {"dish_id": "k4", "dish_name": "French Fries", "veg": True, "price": Decimal("99")},
                        {"dish_id": "k5", "dish_name": "Krusher Brownie", "veg": True, "price": Decimal("149")},
                    ],
                    "subway": [
                        {"dish_id": "s1", "dish_name": "Veggie Delight Sub", "veg": True, "price": Decimal("150")},
                        {"dish_id": "s2", "dish_name": "Paneer Tikka Sub", "veg": True, "price": Decimal("180")},
                        {"dish_id": "s3", "dish_name": "Chicken Teriyaki Sub", "veg": False, "price": Decimal("220")},
                        {"dish_id": "s4", "dish_name": "Aloo Patty Sub", "veg": True, "price": Decimal("160")},
                        {"dish_id": "s5", "dish_name": "Cold Coffee", "veg": True, "price": Decimal("90")},
                    ],
                    "starbucks": [
                        {"dish_id": "sb1", "dish_name": "Cappuccino", "veg": True, "price": Decimal("250")},
                        {"dish_id": "sb2", "dish_name": "Latte", "veg": True, "price": Decimal("230")},
                        {"dish_id": "sb3", "dish_name": "Mocha", "veg": True, "price": Decimal("270")},
                        {"dish_id": "sb4", "dish_name": "Blueberry Muffin", "veg": True, "price": Decimal("150")},
                        {"dish_id": "sb5", "dish_name": "Paneer Sandwich", "veg": True, "price": Decimal("200")},
                    ],
                }
                for menu_list in mock_menus.values():
                    for item in menu_list:
                        if item["dish_id"] == dish_id:
                            menu_item = item
                            break
                    if menu_item:
                        break

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
                        dish_id=menu_item["dish_id"],
                        dish_name=menu_item["dish_name"],
                        dish_price=menu_item["price"],
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

        # Fetch boarding details
        elif action == "fetch_details":
            boarding_pass_number = request.POST.get("boarding_pass_number").strip()
            bd = BoardingDetails.objects(boarding_pass_number=boarding_pass_number).first()
            if not bd:
                return render(request, "core/booking.html", {"username": username, "restaurants": restaurants, "cart": cart, "total": total, "error": "Invalid boarding pass number"})
            if not booking.order:
                return render(request, "core/booking.html", {"username": username, "restaurants": restaurants, "cart": cart, "total": total, "error": "Cart is empty"})
            booking.boarding_pass_number = boarding_pass_number
            booking.location = f"Gate {bd.gate_no} - {bd.departure}"
            booking.status = "Pending"
            booking.date_time = timezone.now()
            booking.save()
            return redirect(reverse("booking_page", kwargs={"username": username}))

        # Reset boarding pass
        elif action == "reset_boarding":
            booking.boarding_pass_number = None
            booking.location = ""
            booking.save()
            return redirect(reverse("booking_page", kwargs={"username": username}))

    return render(request, "core/booking.html", {
        "username": username,
        "restaurants": restaurants,
        "cart": booking.order,
        "total": str(booking.amount),
        "booking": booking
    })


# ------------------------
# Restaurant page
# ------------------------
def restaurant_page(request, username, restaurant_id):
    # Same mock menu as above
    mock_menus = {
        "dominos": [
            {"dish_id": "d1", "dish_name": "Margherita Pizza", "veg": True, "price": 199},
            {"dish_id": "d2", "dish_name": "Veggie Paradise", "veg": True, "price": 249},
            {"dish_id": "d3", "dish_name": "Peppy Paneer", "veg": True, "price": 299},
            {"dish_id": "d4", "dish_name": "Chicken Dominator", "veg": False, "price": 349},
            {"dish_id": "d5", "dish_name": "Garlic Breadsticks", "veg": True, "price": 129},
        ],
        "kfc": [
            {"dish_id": "k1", "dish_name": "Zinger Burger", "veg": False, "price": 199},
            {"dish_id": "k2", "dish_name": "Popcorn Chicken", "veg": False, "price": 249},
            {"dish_id": "k3", "dish_name": "Veg Zinger", "veg": True, "price": 179},
            {"dish_id": "k4", "dish_name": "French Fries", "veg": True, "price": 99},
            {"dish_id": "k5", "dish_name": "Krusher Brownie", "veg": True, "price": 149},
        ],
        "subway": [
            {"dish_id": "s1", "dish_name": "Veggie Delight Sub", "veg": True, "price": 150},
            {"dish_id": "s2", "dish_name": "Paneer Tikka Sub", "veg": True, "price": 180},
            {"dish_id": "s3", "dish_name": "Chicken Teriyaki Sub", "veg": False, "price": 220},
            {"dish_id": "s4", "dish_name": "Aloo Patty Sub", "veg": True, "price": 160},
            {"dish_id": "s5", "dish_name": "Cold Coffee", "veg": True, "price": 90},
        ],
        "starbucks": [
            {"dish_id": "sb1", "dish_name": "Cappuccino", "veg": True, "price": 250},
            {"dish_id": "sb2", "dish_name": "Latte", "veg": True, "price": 230},
            {"dish_id": "sb3", "dish_name": "Mocha", "veg": True, "price": 270},
            {"dish_id": "sb4", "dish_name": "Blueberry Muffin", "veg": True, "price": 150},
            {"dish_id": "sb5", "dish_name": "Paneer Sandwich", "veg": True, "price": 200},
        ],
    }

    restaurant = {
        "name": restaurant_id.capitalize(),
        "menu": mock_menus.get(restaurant_id, [])
    }

    return render(request, "core/restaurant.html", {
        "username": username,
        "restaurant": restaurant
    })


# ------------------------
# Payment page
# ------------------------
@csrf_exempt
def payment_page(request, username, booking_id):
    booking = Booking.objects(booking_id=booking_id, username=username).first()
    if not booking:
        return render(request, "core/payment.html", {"error": "Booking not found"})
    if request.method == "POST":
        payment_method = request.POST.get("payment_method")
        if not payment_method:
            return render(request, "core/payment.html", {"booking": booking, "error": "Select a payment method"})
        transaction_id = f"{username}_{int(datetime.now().timestamp())}"
        Payment(
            transaction_id=transaction_id,
            booking_id=booking.booking_id,
            timestamp=timezone.now(),
            payment_method=payment_method
        ).save()
        booking.status = "Confirmed"
        booking.save()
        return redirect(reverse("orders_page", kwargs={"username": username}))
    return render(request, "core/payment.html", {"booking": booking})


# ------------------------
# Orders page
# ------------------------
def orders_page(request, username):
    confirmed_orders = Booking.objects(username=username, status="Confirmed")
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

    return render(request, "core/orders.html", {
        "orders": confirmed_orders,
        "payments": payments_map,
        "username": username
    })


# ------------------------
# Order history
# ------------------------
def order_history_page(request, username):
    # Fetch completed orders
    completed_orders = Booking.objects(username=username, status="Completed").order_by('-date_time')
    
    # Build a dictionary of payments for easy lookup in template
    payments_dict = {}
    for order in completed_orders:
        payment = Payment.objects(booking_id=order.booking_id).first()
        if payment:
            payments_dict[order.booking_id] = payment
    
    return render(request, "core/orderhistory.html", {
        "username": username,
        "orders": completed_orders,
        "payments": payments_dict  # pass it to template
    })
