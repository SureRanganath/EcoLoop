from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import RegisterForm, ProfileUpdateForm
from .models import UserProfile
from marketplace.models import WasteListing, PurchaseRequest, FavouriteListing


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to EcoLoop, {user.first_name}! Your account has been created.')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect(request.GET.get('next', 'dashboard'))
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    for field in form.fields.values():
        field.widget.attrs['class'] = 'form-control'
    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def dashboard(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profile not found. Please contact support.')
        return redirect('home')

    if profile.is_supplier:
        listings = WasteListing.objects.filter(supplier=request.user).order_by('-created_at')[:5]
        requests_received = PurchaseRequest.objects.filter(
            listing__supplier=request.user
        ).order_by('-created_at')[:5]
        context = {
            'profile': profile,
            'listings': listings,
            'requests_received': requests_received,
            'total_listings': WasteListing.objects.filter(supplier=request.user).count(),
            'active_listings': WasteListing.objects.filter(supplier=request.user, status='available').count(),
            'pending_requests': PurchaseRequest.objects.filter(listing__supplier=request.user, status='pending').count(),
            'completed_exchanges': PurchaseRequest.objects.filter(listing__supplier=request.user, status='completed').count(),
        }
        return render(request, 'accounts/supplier_dashboard.html', context)
    else:
        my_requests = PurchaseRequest.objects.filter(buyer=request.user).order_by('-created_at')[:5]
        favourites = FavouriteListing.objects.filter(user=request.user).select_related('listing')[:5]
        context = {
            'profile': profile,
            'my_requests': my_requests,
            'favourites': favourites,
            'total_requests': PurchaseRequest.objects.filter(buyer=request.user).count(),
            'pending_requests': PurchaseRequest.objects.filter(buyer=request.user, status='pending').count(),
            'completed_exchanges': PurchaseRequest.objects.filter(buyer=request.user, status='completed').count(),
            'saved_listings': FavouriteListing.objects.filter(user=request.user).count(),
        }
        return render(request, 'accounts/buyer_dashboard.html', context)


@login_required
def profile(request):
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profile not found.')
        return redirect('home')

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile, user=request.user)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=user_profile, user=request.user)
    return render(request, 'accounts/profile.html', {'form': form, 'profile': user_profile})
