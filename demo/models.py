from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta


class HealthConditions(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# Table to store meals/recipes
class Meal(models.Model):
    DIET_CHOICES = [
        ('Vegan', 'Vegan'),
        ('Vegetarian', 'Vegetarian'),
        ('Non-Vegetarian', 'Non-Vegetarian'),
    ]
    MEAL_TYPES = [
        ('Breakfast', 'Breakfast'),
        ('Lunch', 'Lunch'),
        ('Dinner', 'Dinner'),
    ]

    name = models.CharField(max_length=100, unique=True)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    diet_suitability = models.CharField(max_length=20, choices=DIET_CHOICES)
    health_condition_suitability = models.ManyToManyField(HealthConditions, blank=True)  # Health conditions for which the meal is suitable
    ingredients = models.TextField()  # Ingredients as a simple text field
    instructions = models.TextField()  # Recipe instructions
    total_cost =models.IntegerField()  # Total cost of the meal
    calories = models.TextField()  # Calories per serving
    fat =  models.TextField()# Fat per serving
    protein =  models.TextField()# Protein per serving
    carbohydrates =  models.TextField() # Carbohydrates per serving
    vitamin_c = models.TextField()  # Vitamin C per serving

    def __str__(self):
        return self.name


# Table to store user preferences and profiles
class UserProfile(models.Model):
    DIET_CHOICES = [
        ('Vegan', 'Vegan'),
        ('Vegetarian', 'Vegetarian'),
        ('Non-Vegetarian', 'Non-Vegetarian'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    height = models.FloatField()
    weight = models.FloatField()
    diet_pref = models.CharField(max_length=200, blank=True, null=True)
    food_allergies = models.CharField(max_length=100, blank=True, null=True)
    health_con = models.ManyToManyField(HealthConditions, blank=True)  # User's health conditions

    def __str__(self):
        return self.user.username

def default_expiration():
    return now() + timedelta(hours=24)

class EmailVerificationCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='verification_code')
    code = models.CharField(max_length=32, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=default_expiration)
    is_valid = models.BooleanField(default=True)

    def is_expired(self):
        return now() > self.expires_at

    def __str__(self):
        return f"Verification Code for {self.user.username}"

class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name