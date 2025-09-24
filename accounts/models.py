from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Listing Model (Property/Accommodation)
class Listing(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return f"{self.title} - {self.location}"


# Booking Model
class Booking(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name='guest_bookings')
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='host_bookings')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    guest_name = models.CharField(max_length=100)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.guest_name} - {self.listing.title}"


# Sample data generator (for testing)
class SampleDataGenerator:
    @staticmethod
    def create_sample_data(user):
        """Create sample listings and bookings for testing"""
        from decimal import Decimal

        # Create sample listings for the user
        listings_data = [
            {'title': 'Cozy Apartment in Dhaka', 'location': 'Dhaka', 'price_per_night': 5000},
            {'title': 'Lakeview House in Sylhet', 'location': 'Sylhet', 'price_per_night': 8000},
            {'title': 'Modern Flat in Chittagong', 'location': 'Chittagong', 'price_per_night': 6500},
        ]

        for data in listings_data:
            Listing.objects.get_or_create(
                owner=user,
                title=data['title'],
                location=data['location'],
                price_per_night=data['price_per_night'],
                defaults={'status': 'active'}
            )

        # Create sample bookings (as host)
        bookings_data = [
            {'guest_name': 'Ayesha Khan', 'check_in_date': '2025-09-28', 'check_out_date': '2025-10-01',
             'total_price': 15000, 'status': 'confirmed'},
            {'guest_name': 'Rahim Ahmed', 'check_in_date': '2025-10-05', 'check_out_date': '2025-10-08',
             'total_price': 24000, 'status': 'confirmed'},
        ]

        # Get user's first listing for bookings
        first_listing = user.listings.first()
        if first_listing:
            for data in bookings_data:
                Booking.objects.get_or_create(
                    host=user,
                    guest=User.objects.first(),  # Use first user as guest
                    listing=first_listing,
                    guest_name=data['guest_name'],
                    check_in_date=data['check_in_date'],
                    check_out_date=data['check_out_date'],
                    total_price=data['total_price'],
                    defaults={'status': data['status']}
                )