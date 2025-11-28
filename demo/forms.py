# demo/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, HealthConditions

class UserProfileForm(forms.ModelForm):
    diet_pref = forms.MultipleChoiceField(
        choices=[
            ('Vegetarian', 'Vegetarian'),
            ('Non-Vegetarian', 'Non-Vegetarian'),
            ('Vegan', 'Vegan'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    food_allergies = forms.ChoiceField(
        choices=[
            ('lactose_intolerance', 'Lactose Intolerance'),
            ('gluten_intolerance', 'Gluten Intolerance'),
            ('fructose_intolerance', 'Fructose Intolerance'),
            ('histamine_intolerance', 'Histamine Intolerance'),
        ],
        widget=forms.Select,
        required=False
    )
    health_con = forms.ModelMultipleChoiceField(
        queryset= HealthConditions.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = UserProfile
        fields = ['name', 'age', 'height', 'weight', 'diet_pref', 'food_allergies', 'health_con']
class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2



class FeedbackForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)
    rating = forms.ChoiceField(choices=[(str(i), str(i)) for i in range(1, 6)], required=True)
