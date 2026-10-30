from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Avg
from django.db.models.functions import TruncMonth
from django.utils import timezone
import json
from marketplace.models import WasteListing, PurchaseRequest, MaterialCategory
from accounts.models import UserProfile


@login_required
def analytics_dashboard(request):
    # Platform-wide stats
    total_listings = WasteListing.objects.count()
    available_listings = WasteListing.objects.filter(status='available').count()
    total_users = User.objects.filter(profile__isnull=False).count()
    total_suppliers = UserProfile.objects.filter(role='supplier').count()
    total_buyers = UserProfile.objects.filter(role='buyer').count()
    total_requests = PurchaseRequest.objects.count()
    completed_exchanges = PurchaseRequest.objects.filter(status='completed').count()

    available_qty = WasteListing.objects.filter(status='available').aggregate(
        total=Sum('quantity'))['total'] or 0
    exchanged_qty = PurchaseRequest.objects.filter(status='completed').aggregate(
        total=Sum('requested_quantity'))['total'] or 0

    # Category distribution
    cat_data = MaterialCategory.objects.annotate(
        count=Count('listings', filter=__import__('django.db.models', fromlist=['Q']).Q(listings__status='available'))
    ).values('name', 'count').order_by('-count')
    cat_labels = [c['name'] for c in cat_data]
    cat_counts = [c['count'] for c in cat_data]

    # Monthly exchange trend (last 12 months)
    twelve_months_ago = timezone.now() - timezone.timedelta(days=365)
    monthly = (
        PurchaseRequest.objects
        .filter(status='completed', created_at__gte=twelve_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'), qty=Sum('requested_quantity'))
        .order_by('month')
    )
    monthly_labels = [m['month'].strftime('%b %Y') for m in monthly]
    monthly_counts = [m['count'] for m in monthly]
    monthly_qty = [float(m['qty'] or 0) for m in monthly]

    # State distribution
    state_data = WasteListing.objects.filter(status='available').values('state').annotate(
        count=Count('id')).order_by('-count')[:10]
    state_labels = [s['state'] for s in state_data]
    state_counts = [s['count'] for s in state_data]

    # Assumption note for environmental estimate
    # Assumption: 1 kg of industrial waste diverted saves approximately 0.5 kg CO2 equivalent
    # This is a rough illustrative estimate, not a verified scientific figure.
    CO2_FACTOR = 0.5
    estimated_co2_saved = float(exchanged_qty) * CO2_FACTOR

    context = {
        'total_listings': total_listings,
        'available_listings': available_listings,
        'total_users': total_users,
        'total_suppliers': total_suppliers,
        'total_buyers': total_buyers,
        'total_requests': total_requests,
        'completed_exchanges': completed_exchanges,
        'available_qty': round(float(available_qty), 2),
        'exchanged_qty': round(float(exchanged_qty), 2),
        'estimated_co2_saved': round(estimated_co2_saved, 2),
        'cat_labels': json.dumps(cat_labels),
        'cat_counts': json.dumps(cat_counts),
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_counts': json.dumps(monthly_counts),
        'monthly_qty': json.dumps(monthly_qty),
        'state_labels': json.dumps(state_labels),
        'state_counts': json.dumps(state_counts),
    }
    return render(request, 'analytics/dashboard.html', context)
