from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile

INDIAN_STATES = [
    ('', 'Select State'),
    ('Andhra Pradesh', 'Andhra Pradesh'), ('Arunachal Pradesh', 'Arunachal Pradesh'),
    ('Assam', 'Assam'), ('Bihar', 'Bihar'), ('Chhattisgarh', 'Chhattisgarh'),
    ('Goa', 'Goa'), ('Gujarat', 'Gujarat'), ('Haryana', 'Haryana'),
    ('Himachal Pradesh', 'Himachal Pradesh'), ('Jharkhand', 'Jharkhand'),
    ('Karnataka', 'Karnataka'), ('Kerala', 'Kerala'), ('Madhya Pradesh', 'Madhya Pradesh'),
    ('Maharashtra', 'Maharashtra'), ('Manipur', 'Manipur'), ('Meghalaya', 'Meghalaya'),
    ('Mizoram', 'Mizoram'), ('Nagaland', 'Nagaland'), ('Odisha', 'Odisha'),
    ('Punjab', 'Punjab'), ('Rajasthan', 'Rajasthan'), ('Sikkim', 'Sikkim'),
    ('Tamil Nadu', 'Tamil Nadu'), ('Telangana', 'Telangana'), ('Tripura', 'Tripura'),
    ('Uttar Pradesh', 'Uttar Pradesh'), ('Uttarakhand', 'Uttarakhand'),
    ('West Bengal', 'West Bengal'), ('Delhi', 'Delhi'),
]


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES)
    company_name = forms.CharField(max_length=200)
    industry_type = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=20, required=False)
    city = forms.CharField(max_length=100)
    state = forms.ChoiceField(choices=INDIAN_STATES)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                role=self.cleaned_data['role'],
                company_name=self.cleaned_data['company_name'],
                industry_type=self.cleaned_data['industry_type'],
                phone=self.cleaned_data.get('phone', ''),
                city=self.cleaned_data['city'],
                state=self.cleaned_data['state'],
            )
        return user


class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()

    class Meta:
        model = UserProfile
        fields = ['company_name', 'industry_type', 'phone', 'city', 'state', 'address', 'website', 'bio', 'avatar']
        widgets = {'state': forms.Select(choices=INDIAN_STATES)}

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
