from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),  # Main dashboard
    path('my-listings/', views.my_listings, name='my_listings'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('create-listing/', views.create_listing, name='create_listing'),
    path('logout/', views.logout_view, name='logout'),
]