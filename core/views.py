from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from marketplace.models import WasteListing, MaterialCategory, PurchaseRequest
from accounts.models import UserProfile
from django.db.models import Count, Sum


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    recent_listings = WasteListing.objects.filter(status='available').select_related('category', 'supplier__profile')[:6]
    categories = MaterialCategory.objects.annotate(count=Count('listings')).order_by('-count')[:6]
    stats = {
        'total_listings': WasteListing.objects.filter(status='available').count(),
        'total_suppliers': UserProfile.objects.filter(role='supplier').count(),
        'total_buyers': UserProfile.objects.filter(role='buyer').count(),
        'completed_exchanges': PurchaseRequest.objects.filter(status='completed').count(),
    }
    return render(request, 'core/home.html', {'recent_listings': recent_listings, 'categories': categories, 'stats': stats})


def about(request):
    tech_stack = [
        ('Python 3.14', 'Backend programming language'),
        ('Django 5.1', 'Web framework with ORM, auth, and admin'),
        ('SQLite', 'Lightweight relational database'),
        ('Bootstrap 5', 'Responsive CSS framework'),
        ('scikit-learn', 'TF-IDF and ML recommendation engine'),
        ('pandas / NumPy', 'Data processing and numerical computing'),
        ('Chart.js', 'Interactive analytics charts'),
        ('python-dotenv', 'Environment-based configuration'),
    ]
    return render(request, 'core/about.html', {'tech_stack': tech_stack})


def error_403(request, exception=None):
    return render(request, 'errors/403.html', status=403)


def error_404(request, exception=None):
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    return render(request, 'errors/500.html', status=500)
