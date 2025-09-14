from django.db import models

# Create your models here.

# core.models.py
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
    boarding_pass_number = StringField(primary_key=True)
    flight_no = StringField(required=True)
    departure = StringField(required=True)
    arrival = StringField(required=True)
    gate_no = StringField(required=True)

    meta = {'collection': 'boarding_details'}


# ========================
# Table 2: Booking
# ========================
class Booking(Document):
    booking_id = StringField(primary_key=True)
    username = StringField(required=True)  # FK → User.username
    status = StringField(
        required=True,
        choices=["Pending", "Confirmed", "Completed", "Cancelled"],
        default="Pending"
    )
    date_time = DateTimeField(required=True)
    location = StringField(required=True)
    amount = FloatField(required=True)
    boarding_pass_number = StringField(required=True)  # FK → BoardingDetails
    restaurant_id = StringField()  # Future FK
    delivery_partner_id = StringField()  # Future FK

    meta = {'collection': 'bookings'}


# ========================
# Table 4: Payment
# ========================
class Payment(Document):
    transaction_id = StringField(primary_key=True)
    booking_id = StringField(required=True)  # FK → Booking.booking_id
    timestamp = DateTimeField(required=True)
    payment_method = StringField(required=True)  # UPI | Card | Wallet | Cash etc.

    meta = {'collection': 'payments'}
