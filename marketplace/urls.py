from django.urls import path
from . import views

urlpatterns = [
    path('', views.marketplace, name='marketplace'),
    path('listing/<int:pk>/', views.listing_detail, name='listing_detail'),
    path('listing/add/', views.add_listing, name='add_listing'),
    path('listing/<int:pk>/edit/', views.edit_listing, name='edit_listing'),
    path('listing/<int:pk>/delete/', views.delete_listing, name='delete_listing'),
    path('listing/<int:pk>/request/', views.submit_request, name='submit_request'),
    path('listing/<int:pk>/favourite/', views.toggle_favourite, name='toggle_favourite'),
    path('requests/', views.my_requests, name='my_requests'),
    path('requests/<int:pk>/update/', views.update_request_status, name='update_request_status'),
    path('requests/<int:pk>/cancel/', views.cancel_request, name='cancel_request'),
    path('favourites/', views.favourites, name='favourites'),
    path('transactions/', views.transaction_history, name='transaction_history'),
    path('contact/', views.contact, name='contact'),
]
