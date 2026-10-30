from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse
from django.db.models import Q
from .models import WasteListing, MaterialCategory, PurchaseRequest, FavouriteListing, ContactMessage
from .forms import WasteListingForm, PurchaseRequestForm, ContactForm, MarketplaceFilterForm
from accounts.models import UserProfile


def marketplace(request):
    listings = WasteListing.objects.filter(status='available').select_related('supplier__profile', 'category')
    form = MarketplaceFilterForm(request.GET)
    categories = MaterialCategory.objects.all()

    if form.is_valid():
        q = form.cleaned_data.get('q')
        category = form.cleaned_data.get('category')
        state = form.cleaned_data.get('state')
        min_qty = form.cleaned_data.get('min_qty')
        max_price = form.cleaned_data.get('max_price')
        sort = form.cleaned_data.get('sort', 'newest')

        if q:
            listings = listings.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(category__name__icontains=q))
        if category:
            listings = listings.filter(category__slug=category)
        if state:
            listings = listings.filter(state=state)
        if min_qty:
            listings = listings.filter(quantity__gte=min_qty)
        if max_price:
            listings = listings.filter(price_per_kg__lte=max_price)

        sort_map = {
            'newest': '-created_at', 'oldest': 'created_at',
            'price_asc': 'price_per_kg', 'price_desc': '-price_per_kg',
            'qty_desc': '-quantity',
        }
        listings = listings.order_by(sort_map.get(sort, '-created_at'))

    paginator = Paginator(listings, 12)
    page = paginator.get_page(request.GET.get('page'))

    favourites = set()
    if request.user.is_authenticated:
        favourites = set(FavouriteListing.objects.filter(user=request.user).values_list('listing_id', flat=True))

    return render(request, 'marketplace/marketplace.html', {
        'page_obj': page,
        'form': form,
        'categories': categories,
        'favourites': favourites,
        'total_count': listings.count(),
    })


def listing_detail(request, pk):
    listing = get_object_or_404(WasteListing.objects.select_related('supplier__profile', 'category'), pk=pk)
    is_favourite = False
    user_request = None

    if request.user.is_authenticated:
        is_favourite = FavouriteListing.objects.filter(user=request.user, listing=listing).exists()
        try:
            user_request = PurchaseRequest.objects.filter(buyer=request.user, listing=listing).latest('created_at')
        except PurchaseRequest.DoesNotExist:
            pass

    related = WasteListing.objects.filter(
        category=listing.category, status='available'
    ).exclude(pk=listing.pk)[:4]

    return render(request, 'marketplace/listing_detail.html', {
        'listing': listing,
        'is_favourite': is_favourite,
        'user_request': user_request,
        'related': related,
    })


@login_required
def add_listing(request):
    try:
        profile = request.user.profile
        if not profile.is_supplier:
            messages.error(request, 'Only suppliers can create listings.')
            return redirect('marketplace')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profile not found.')
        return redirect('home')

    if request.method == 'POST':
        form = WasteListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.supplier = request.user
            listing.save()
            messages.success(request, 'Listing created successfully!')
            return redirect('listing_detail', pk=listing.pk)
    else:
        form = WasteListingForm()
    return render(request, 'marketplace/listing_form.html', {'form': form, 'action': 'Add'})


@login_required
def edit_listing(request, pk):
    listing = get_object_or_404(WasteListing, pk=pk)
    if listing.supplier != request.user:
        messages.error(request, 'You are not authorised to edit this listing.')
        return redirect('listing_detail', pk=pk)

    if request.method == 'POST':
        form = WasteListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            form.save()
            messages.success(request, 'Listing updated successfully!')
            return redirect('listing_detail', pk=listing.pk)
    else:
        form = WasteListingForm(instance=listing)
    return render(request, 'marketplace/listing_form.html', {'form': form, 'action': 'Edit', 'listing': listing})


@login_required
def delete_listing(request, pk):
    listing = get_object_or_404(WasteListing, pk=pk)
    if listing.supplier != request.user:
        messages.error(request, 'You are not authorised to delete this listing.')
        return redirect('listing_detail', pk=pk)
    if request.method == 'POST':
        listing.delete()
        messages.success(request, 'Listing deleted.')
        return redirect('dashboard')
    return render(request, 'marketplace/confirm_delete.html', {'listing': listing})


@login_required
def submit_request(request, pk):
    listing = get_object_or_404(WasteListing, pk=pk, status='available')
    try:
        profile = request.user.profile
        if not profile.is_buyer:
            messages.error(request, 'Only buyers can submit purchase requests.')
            return redirect('listing_detail', pk=pk)
    except UserProfile.DoesNotExist:
        return redirect('home')

    if listing.supplier == request.user:
        messages.error(request, 'You cannot request your own listing.')
        return redirect('listing_detail', pk=pk)

    if request.method == 'POST':
        form = PurchaseRequestForm(request.POST, listing=listing)
        if form.is_valid():
            with transaction.atomic():
                pr = form.save(commit=False)
                pr.buyer = request.user
                pr.listing = listing
                pr.save()
            messages.success(request, 'Purchase request submitted successfully!')
            return redirect('my_requests')
    else:
        form = PurchaseRequestForm(listing=listing)
    return render(request, 'marketplace/request_form.html', {'form': form, 'listing': listing})


@login_required
def my_requests(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        return redirect('home')

    if profile.is_buyer:
        requests_qs = PurchaseRequest.objects.filter(buyer=request.user).select_related('listing__category', 'listing__supplier__profile')
    else:
        requests_qs = PurchaseRequest.objects.filter(listing__supplier=request.user).select_related('listing__category', 'buyer__profile')

    paginator = Paginator(requests_qs, 10)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'marketplace/requests.html', {'page_obj': page, 'profile': profile})


@login_required
def update_request_status(request, pk):
    pr = get_object_or_404(PurchaseRequest, pk=pk)
    if pr.listing.supplier != request.user:
        messages.error(request, 'Not authorised.')
        return redirect('my_requests')

    new_status = request.POST.get('status')
    if new_status in ['accepted', 'rejected', 'completed']:
        pr.status = new_status
        pr.save()
        messages.success(request, f'Request {new_status}.')
    return redirect('my_requests')


@login_required
def cancel_request(request, pk):
    pr = get_object_or_404(PurchaseRequest, pk=pk, buyer=request.user)
    if pr.status == 'pending':
        pr.status = 'cancelled'
        pr.save()
        messages.success(request, 'Request cancelled.')
    return redirect('my_requests')


@login_required
def toggle_favourite(request, pk):
    listing = get_object_or_404(WasteListing, pk=pk)
    fav, created = FavouriteListing.objects.get_or_create(user=request.user, listing=listing)
    if not created:
        fav.delete()
        action = 'removed'
    else:
        action = 'added'
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'action': action})
    return redirect('listing_detail', pk=pk)


@login_required
def favourites(request):
    favs = FavouriteListing.objects.filter(user=request.user).select_related('listing__category', 'listing__supplier__profile')
    return render(request, 'marketplace/favourites.html', {'favourites': favs})


@login_required
def transaction_history(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        return redirect('home')

    if profile.is_buyer:
        completed = PurchaseRequest.objects.filter(buyer=request.user, status='completed').select_related('listing__category', 'listing__supplier__profile')
    else:
        completed = PurchaseRequest.objects.filter(listing__supplier=request.user, status='completed').select_related('listing__category', 'buyer__profile')

    return render(request, 'marketplace/transactions.html', {'transactions': completed, 'profile': profile})


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent. We will get back to you soon!')
            return redirect('contact')
    else:
        form = ContactForm()
        if request.user.is_authenticated:
            form.fields['name'].initial = request.user.get_full_name()
            form.fields['email'].initial = request.user.email
    return render(request, 'core/contact.html', {'form': form})
