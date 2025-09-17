"""
URL configuration for aireats project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


#aireats/urls.py
from django.contrib import admin
from django.urls import path
from core import views
from django.shortcuts import render

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.home, name='home'),

    # HTML pages
    path("login/", views.login_view, name="login_page"),
    path("signup/", views.signup, name="signup_page"),

    # Booking page (username passed in URL)
    path("booking/<str:username>/", views.booking_page, name="booking_page"),
    path("booking/<str:username>/restaurant/<str:restaurant_id>/", views.restaurant_page, name="restaurant_page"),

    # Payment + Orders
    path("payment/<str:username>/<str:booking_id>/", views.payment_page, name="payment_page"),
    path("orders/<str:username>/", views.orders_page, name="orders_page"),

    # Orders
    path("orderhistory/<str:username>/", views.order_history_page, name="order_history_page"),
]

