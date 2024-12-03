 
import json
from collections import defaultdict
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect
from django.core.paginator import Paginator



from schedules.forms import SearchForm
from schedules.models import Booking
from schedules.models import Schedule
from .forms import UserRegisterForm, UserLoginForm
from .models import UserProfile


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            balance=form.cleaned_data.get('balance')
            user = User.objects.create(username=username, email=email, password=make_password(password))
            UserProfile.objects.create(user=user,balance=balance)
            login(request, user)
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, "Invalid username or password")
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')




@login_required
def home(request):
    user_profile = UserProfile.objects.get(user=request.user)
    schedules = None
    search_form = SearchForm()

    # Retrieve bookings for the current user
    booked = Booking.objects.filter(user=request.user)
    bookedStatistics = defaultdict(int)

    # Group bookings by the day and count them
    for booking in booked:
        day_label = booking.created_at.strftime('%Y-%m-%d')
        bookedStatistics[day_label] += 1

    # Prepare data for Chart.js
    labels = list(bookedStatistics.keys())
    booked_counts = list(bookedStatistics.values())

    if request.method == 'POST':
        search_form = SearchForm(request.POST)
        if search_form.is_valid():
            query = search_form.cleaned_data['query'].lower()  # Convert the query to lowercase
            schedules = Schedule.objects.filter(
                Q(company__name__icontains=query) |
                Q(route__source__name__icontains=query) |
                Q(route__destination__name__icontains=query)
            )
    else:
        schedules = Schedule.objects.all()

    paginator = Paginator(schedules, 10)  # Show 10 schedules per page
    page_number = request.GET.get('page')
    page_object = paginator.get_page(page_number)

    # Pagination for booked tickets
    booked_paginator = Paginator(booked, 10)  # Show 5 bookings per page
    booked_page_number = request.GET.get('booked_page')
    booked_object = booked_paginator.get_page(booked_page_number)

    context = {
        'schedules': page_object,
        'booked_ticket': booked_object,
        'search_form': search_form,
        'booked_statistics': json.dumps({
            'labels': labels,
            'booked_counts': booked_counts
        }),
    }

    return render(request, 'users/home.html', context)
