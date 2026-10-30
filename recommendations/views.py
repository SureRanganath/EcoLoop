from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from marketplace.models import WasteListing, MaterialCategory
from accounts.models import UserProfile
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from ml.recommender import get_recommendations, suggest_category
from accounts.forms import INDIAN_STATES


class RecommendationForm(forms.Form):
    query = forms.CharField(
        label='Describe the material you need',
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'e.g. recyclable plastic scraps for manufacturing...'}),
    )
    category = forms.ModelChoiceField(
        queryset=MaterialCategory.objects.all(),
        required=False,
        empty_label='Any Category',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    quantity = forms.DecimalField(
        label='Quantity needed (kg)',
        min_value=0.1,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 500'}),
    )
    max_price = forms.DecimalField(
        label='Max price per kg (₹)',
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 50'}),
    )
    state = forms.ChoiceField(
        choices=[('', 'Any State')] + INDIAN_STATES[1:],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )


class CategorySuggestForm(forms.Form):
    description = forms.CharField(
        label='Material description',
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Describe the material...'}),
    )


@login_required
def recommendations_view(request):
    form = RecommendationForm(request.GET or None)
    results = []
    searched = False

    if form.is_valid():
        searched = True
        listings = WasteListing.objects.filter(status='available')
        # Exclude supplier's own listings
        try:
            if request.user.profile.is_supplier:
                listings = listings.exclude(supplier=request.user)
        except UserProfile.DoesNotExist:
            pass

        results = get_recommendations(
            query_text=form.cleaned_data['query'],
            category_id=form.cleaned_data['category'].id if form.cleaned_data.get('category') else None,
            requested_qty=form.cleaned_data.get('quantity') or 1,
            max_budget=form.cleaned_data.get('max_price'),
            preferred_state=form.cleaned_data.get('state'),
            listings=listings,
            top_n=10,
        )

    return render(request, 'recommendations/recommendations.html', {
        'form': form,
        'results': results,
        'searched': searched,
        'weights': {'Text Similarity': 35, 'Category Match': 25, 'Quantity': 15, 'Location': 15, 'Price': 10},
    })


@login_required
def suggest_category_view(request):
    form = CategorySuggestForm(request.POST or None)
    suggestion = None
    confidence = None

    if request.method == 'POST' and form.is_valid():
        text = form.cleaned_data['description']
        try:
            suggestion, confidence = suggest_category(text)
        except Exception as e:
            messages.error(request, f'Could not suggest category: {e}')

    return render(request, 'recommendations/suggest_category.html', {
        'form': form,
        'suggestion': suggestion,
        'confidence': confidence,
    })
