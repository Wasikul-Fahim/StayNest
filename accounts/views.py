from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta
import re
from decimal import Decimal
from .models import Listing, Booking, SampleDataGenerator
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings


# Forgot Password View
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()

        # Check if email exists (use username since username=email and unique)
        try:
            user = User.objects.get(username=email)

            # Generate password reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Create reset link
            reset_link = request.build_absolute_uri(
                f'/reset-password/{uid}/{token}/'
            )

            # Prepare email
            subject = 'Reset Your Staynest Password'
            message = f"""
Hello {user.first_name or user.username},

You requested to reset your password for your Staynest account.

Click the link below to reset your password:
{reset_link}

This link will expire in 24 hours.

If you didn't request this, please ignore this email.

Best regards,
Staynest Team
            """

            # Send email
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                messages.success(
                    request,
                    f"Password reset link has been sent to {email}. Please check your inbox."
                )
            except Exception as e:
                messages.error(
                    request,
                    "Failed to send email. Please try again later."
                )
                print(f"Email error: {e}")  # Terminal এ error দেখাবে

            return redirect('forgot_password')

        except User.DoesNotExist:
            messages.error(request, "No account found with this email address!")

    return render(request, 'forgot_password.html')


# Reset Password Confirm View
def reset_password_confirm(request, uidb64, token):
    try:
        # Decode user id
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        # Verify token
        if default_token_generator.check_token(user, token):
            if request.method == 'POST':
                new_password = request.POST.get('new_password')
                confirm_password = request.POST.get('confirm_password')

                # Check if passwords match
                if new_password != confirm_password:
                    messages.error(request, "Passwords do not match!")
                    return render(request, 'reset_password_confirm.html')

                # Validate password
                is_valid, message = is_valid_password(new_password)
                if not is_valid:
                    messages.error(request, f"Password requirements: {message}")
                    return render(request, 'reset_password_confirm.html')

                # Set new password
                user.set_password(new_password)
                user.save()

                messages.success(request, "Password reset successful! You can now login with your new password.")
                return redirect('login')

            return render(request, 'reset_password_confirm.html')
        else:
            messages.error(request, "Invalid or expired reset link!")
            return redirect('forgot_password')

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, "Invalid reset link!")
        return redirect('forgot_password')
# Helper function for password validation
def is_valid_password(password):
    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")

    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter (A-Z).")

    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter (a-z).")

    if not re.search(r'\d', password):
        errors.append("Password must contain at least one number (0-9).")

    if not re.search(r'[!@#$%^&*]', password):
        errors.append("Password must contain at least one special character (!@#$%^&*).")

    if errors:
        return False, "; ".join(errors)
    return True, "Password is valid."


# Navbar



# Home page
def home(request):
    return render(request, 'home.html')

def hm(request): 
    return render(request, 'hm.html')


# Login view - Redirect to dashboard
def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect('dashboard')  # Changed to dashboard
        else:
            messages.error(request, "Invalid email or password! Please try again.")

    return render(request, 'login.html')


# Signup view - Redirect to dashboard + create sample data
def signup_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # Basic validation
        if not all([full_name, email, password, confirm_password]):
            messages.error(request, "All fields are required!")
            return render(request, 'signup.html')

        # Check passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match! Please enter the same password.")
            return render(request, 'signup.html')

        # Email validation
        email_pattern = r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
        if not re.match(email_pattern, email):
            messages.error(request, "Please enter a valid email address.")
            return render(request, 'signup.html')

        # Password validation
        is_valid, message = is_valid_password(password)
        if not is_valid:
            messages.error(request, f"Password requirements: {message}")
            return render(request, 'signup.html')

        # Check if user already exists
        if User.objects.filter(username=email).exists():
            messages.error(request, "User with this email already exists! Please use a different email.")
            return render(request, 'signup.html')

        # Create user
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password
            )
            user.first_name = full_name
            user.save()

            # Create sample data for new user
            SampleDataGenerator.create_sample_data(user)

            # Auto login
            login(request, user)
            messages.success(request, f"Welcome to Staynest, {full_name}! Your account has been created.")
            return redirect('dashboard')  # Changed to dashboard
        except Exception as e:
            messages.error(request, f"Error creating account. Please try again.")
            return render(request, 'signup.html')

    return render(request, 'signup.html')


# NEW: Dashboard View
@login_required
def dashboard(request):
    user = request.user

    # Get current month and previous month earnings
    current_month = timezone.now().month
    current_year = timezone.now().year
    prev_month = current_month - 1 if current_month > 1 else 12
    prev_year = current_year if current_month > 1 else current_year - 1

    # Calculate earnings (simplified - in real app, you'd calculate from completed bookings)
    current_month_earnings = Decimal('41900')  # Sample data
    prev_month_earnings = Decimal('38000')  # Sample data
    earnings_change = ((
                                   current_month_earnings - prev_month_earnings) / prev_month_earnings * 100) if prev_month_earnings > 0 else 0

    # Get user's listings
    user_listings = user.listings.all()[:3]  # Show first 3 listings

    # Get upcoming stays (bookings where user is host)
    upcoming_stays = Booking.objects.filter(
        host=user,
        status='confirmed',
        check_in_date__gte=timezone.now().date()
    ).order_by('check_in_date')[:3]

    # Get upcoming bookings (where user is guest)
    upcoming_bookings = Booking.objects.filter(
        guest=user,
        status='confirmed',
        check_in_date__gte=timezone.now().date()
    ).order_by('check_in_date')[:3]

    # Calculate occupancy rate (simplified)
    total_listings = user.listings.count()
    occupancy_rate = min(100, (total_listings * 20)) if total_listings > 0 else 0  # Sample calculation

    # Calculate spending (simplified)
    current_month_spending = Decimal('2900')  # Sample data
    prev_month_spending = Decimal('3500')  # Sample data
    spending_change = ((
                                   current_month_spending - prev_month_spending) / prev_month_spending * 100) if prev_month_spending > 0 else 0

    # Total bookings count
    total_bookings = Booking.objects.filter(host=user).count()

    # Get greeting
    hour = timezone.now().hour
    if 5 <= hour < 12:
        greeting = "Good morning"
    elif 12 <= hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    context = {
        'user': user,
        'greeting': f"{greeting}, {user.first_name or user.username.split('@')[0].title()}!",
        'current_month_earnings': current_month_earnings,
        'prev_month_earnings': prev_month_earnings,
        'earnings_change': earnings_change,
        'occupancy_rate': occupancy_rate,
        'current_month_spending': current_month_spending,
        'prev_month_spending': prev_month_spending,
        'spending_change': spending_change,
        'total_bookings': total_bookings,
        'user_listings': user_listings,
        'upcoming_stays': upcoming_stays,
        'upcoming_bookings': upcoming_bookings,
    }

    return render(request, 'dashboard.html', context)


# Logout View
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully!")
    return redirect('home')


# My Listings View
@login_required
def my_listings(request):
    user_listings = request.user.listings.all()
    context = {
        'listings': user_listings,
        'section_title': 'My Listings'
    }
    return render(request, 'listings.html', context)


# My Bookings View
@login_required
def my_bookings(request):
    user_bookings = Booking.objects.filter(guest=request.user)
    context = {
        'bookings': user_bookings,
        'section_title': 'My Bookings'
    }
    return render(request, 'bookings.html', context)


# Create Listing View (Basic form)
@login_required
def create_listing(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        location = request.POST.get('location')
        price_per_night = request.POST.get('price_per_night')

        if title and location and price_per_night:
            Listing.objects.create(
                owner=request.user,
                title=title,
                location=location,
                price_per_night=Decimal(price_per_night),
                status='active'
            )
            messages.success(request, 'Listing created successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please fill all fields!')

    return render(request, 'create_listing.html')