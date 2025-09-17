from django.db import models

# Create your models here.

# core/models.py
from mongoengine import Document, StringField, EmailField, IntField, DateField, EmbeddedDocument, EmbeddedDocumentField, FloatField, DateTimeField

# ------------------------
# Embedded Name Field
# ------------------------
class Name(EmbeddedDocument):
    first_name = StringField(required=True, max_length=50)
    last_name = StringField(required=True, max_length=50)


# ========================
# Table 1: User
# ========================
class User(Document):
    username = StringField(unique=True, required=True, max_length=50)
    password = StringField(required=True)   # will hash later
    name = EmbeddedDocumentField(Name, required=True)
    email = EmailField(required=True, unique=True)
    phone = StringField(required=True, unique=True)
    role = IntField(required=True, choices=[1, 2, 3])  # 1=Customer, 2=Delivery Partner, 3+ Future

    # Optional fields
    sex = StringField(choices=["Male", "Female", "Other"])
    dob = DateField()
    nationality = StringField()
    address = StringField()

    meta = {'collection': 'users'}


# ========================
# Table 3: Boarding Details
# ========================
class BoardingDetails(Document):
    boarding_pass_number = StringField(unique=True,required=True)
    flight_no = StringField(required=True)
    departure = StringField(required=True)
    arrival = StringField(required=True)
    gate_no = StringField(required=True)

    meta = {'collection': 'boarding_details'}


# ========================
# Table 4: Payment
# ========================
class Payment(Document):
    transaction_id = StringField(unique=True,required=True)
    booking_id = StringField(required=True)  # FK → Booking.booking_id
    timestamp = DateTimeField(required=True)
    payment_method = StringField(required=True)  # UPI | Card | Wallet | Cash etc.

    meta = {'collection': 'payments'}


# ========================
# Table 5: Menu & Booking
# ========================
from mongoengine import Document, EmbeddedDocument, fields
from decimal import Decimal

# ----------------------
# Menu Collection (each document = 1 dish)
# ----------------------
class Menu(Document):
    restaurant_id = fields.StringField(required=True)
    restaurant_name = fields.StringField(required=True)
    
    dish_id = fields.StringField(required=True, unique=True)  # globally unique
    dish_name = fields.StringField(required=True)
    veg = fields.BooleanField(default=True)  # True = veg, False = non-veg
    price = fields.DecimalField(required=True, precision=2)  # safer for money
    category = fields.StringField()  # optional
    cuisine = fields.StringField()   # optional
    description = fields.StringField()  # optional

    meta = {'collection': 'menu'}


# ----------------------
# Order Item (embedded in Booking)
# ----------------------
class OrderItem(EmbeddedDocument):
    dish_id = fields.StringField(required=True)
    dish_name = fields.StringField(required=True)
    dish_price = fields.DecimalField(required=True, precision=2)
    quantity = fields.IntField(required=True, min_value=1)


# ----------------------
# Table 2: Booking Collection
# ----------------------
class Booking(Document):
    booking_id = fields.StringField(primary_key=True)
    username = fields.StringField(required=True)  # FK → User.username
    status = fields.StringField(
        required=True,
        choices=["Pending", "Confirmed", "Completed", "Cancelled"],
        default="Pending"
    )
    date_time = fields.DateTimeField(required=True)
    location = fields.StringField(required=True)
    restaurant_id = fields.StringField()  # FK → Menu.restaurant_id
    delivery_partner_id = fields.StringField()  # optional
    boarding_pass_number = fields.StringField(required=False)  # FK → BoardingDetails.boarding_pass_number

    # Embedded order items
    order = fields.ListField(fields.EmbeddedDocumentField(OrderItem))

    # Total amount (must be set by API, not auto-calculated here)
    amount = fields.DecimalField(required=True, precision=2, default=Decimal('0.00'))

    meta = {'collection': 'bookings'}
