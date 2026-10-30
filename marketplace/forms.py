from django import forms
from .models import WasteListing, PurchaseRequest, ContactMessage
from accounts.forms import INDIAN_STATES


class WasteListingForm(forms.ModelForm):
    class Meta:
        model = WasteListing
        fields = ['title', 'category', 'description', 'quantity', 'price_per_kg',
                  'quality_grade', 'city', 'state', 'image', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'state': forms.Select(choices=INDIAN_STATES),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'

    def clean_quantity(self):
        qty = self.cleaned_data.get('quantity')
        if qty is not None and qty <= 0:
            raise forms.ValidationError('Quantity must be greater than zero.')
        return qty

    def clean_price_per_kg(self):
        price = self.cleaned_data.get('price_per_kg')
        if price is not None and price < 0:
            raise forms.ValidationError('Price cannot be negative.')
        return price


class PurchaseRequestForm(forms.ModelForm):
    class Meta:
        model = PurchaseRequest
        fields = ['requested_quantity', 'proposed_price', 'message']
        widgets = {'message': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, listing=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.listing = listing
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        if listing:
            self.fields['requested_quantity'].help_text = f'Available: {listing.quantity} kg'
            self.fields['proposed_price'].help_text = f'Listed price: ₹{listing.price_per_kg}/kg'

    def clean_requested_quantity(self):
        qty = self.cleaned_data.get('requested_quantity')
        if self.listing and qty and qty > self.listing.quantity:
            raise forms.ValidationError(f'Cannot exceed available quantity of {self.listing.quantity} kg.')
        if qty and qty <= 0:
            raise forms.ValidationError('Quantity must be greater than zero.')
        return qty


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {'message': forms.Textarea(attrs={'rows': 5})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class MarketplaceFilterForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Search materials...', 'class': 'form-control'}))
    category = forms.CharField(required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    state = forms.ChoiceField(choices=[('', 'All States')] + INDIAN_STATES[1:], required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    min_qty = forms.DecimalField(required=False, min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min qty (kg)'}))
    max_price = forms.DecimalField(required=False, min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max price/kg'}))
    sort = forms.ChoiceField(
        choices=[('newest', 'Newest First'), ('oldest', 'Oldest First'), ('price_asc', 'Price: Low to High'),
                 ('price_desc', 'Price: High to Low'), ('qty_desc', 'Quantity: High to Low')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
