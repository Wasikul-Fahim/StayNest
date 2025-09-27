from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
def home(request):
    return render(request, "home.html")

def dashboard(request):
    context = {
        "user_name": "Jane",
        "earnings": 41900,
        "earnings_growth": "+15% from last month",
        "occupancy": 80,
        "spendings": 2900,
        "spendings_change": "-2% from last month",
        "upcoming_bookings": 12,
        "upcoming_stays": [
            {"guest": "Akif Hossain", "dates": "28 Sep -", "listing": "Mohammadpur", "status": "Checked In"},
            {"guest": "Fabia Tasnim", "dates": "1 Aug -", "listing": "Mohammadpur", "status": "Arriving"},
        ],
        "upcoming_rentals": [
            {"listing": "Dhanmondi", "dates": "1 Sep -", "rent": "38,000৳", "status": "Checked In"},
        ],
    }
    return render(request, "dashboard.html", context)
