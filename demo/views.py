from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import Meal, UserProfile, HealthConditions
from .forms import SignUpForm, UserProfileForm, User
# demo/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import EmailVerificationCode
from .forms import SignUpForm
from .utils import generate_otp, send_otp_email
from django.contrib.auth import logout
from .models import Feedback
from .forms import FeedbackForm

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']

            # Check if passwords match
            if password1 != password2:
                messages.error(request, "Passwords do not match!")
                return redirect('signup')

            # Check if the email is already in use
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email is already registered!")
                return redirect('signup')

            # Create and save user
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.is_active = False  # Deactivate account till it is confirmed
            user.save()

            # Generate and send OTP
            otp = generate_otp()
            EmailVerificationCode.objects.create(user=user, code=otp)
            send_otp_email(user, otp)

            request.session['user_id'] = user.id
            return redirect('verify_otp')
    else:
        form = SignUpForm()
    return render(request, 'demo/signup.html', {'form': form})

def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        user_id = request.session.get('user_id')
        user = User.objects.get(id=user_id)
        otp_obj = EmailVerificationCode.objects.get(user=user)

        if otp_obj.code == otp and not otp_obj.is_expired():
            user.is_active = True
            user.save()
            otp_obj.is_valid = False
            otp_obj.save()
            messages.success(request, "Your email has been verified. Please log in.")
            return redirect('login')
        else:
            messages.error(request, "Invalid or expired OTP.")
            return render(request, 'demo/verify_otp.html')
    return render(request, 'demo/verify_otp.html')

# Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")  # Optional: welcome message
            return redirect('home')  # Redirect to the home page after successful login
        else:
            messages.error(request, "Invalid credentials!")
            return redirect('login')

    return render(request, 'demo/login.html')

# Home View

def home_view(request):
    return render(request, 'demo/home.html', {'username': request.user.username})

# User profile view (form submission)

def user_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            user_profile, created = UserProfile.objects.update_or_create(
                user=request.user,  # Associate the form data with the logged-in user
                defaults={
                    'name': form.cleaned_data['name'],
                    'age': form.cleaned_data['age'],
                    'height': form.cleaned_data['height'],
                    'weight': form.cleaned_data['weight'],
                    'diet_pref': form.cleaned_data['diet_pref'],
                    'food_allergies': form.cleaned_data['food_allergies'],
                }
            )
            # Use the set() method to update the many-to-many relationship
            user_profile.health_con.set(form.cleaned_data['health_con'])
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile_success')  # Redirect to the success page
        else:
            messages.error(request, "There was an error with your submission.")
    else:
        user_profile = UserProfile.objects.filter(user=request.user).first()
        if user_profile:
            form = UserProfileForm(instance=user_profile)
        else:
            form = UserProfileForm()
    return render(request, 'demo/userprofile.html', {'form': form})

# Profile success view
def profile_success(request):
    return render(request, 'demo/profilesuc.html')


def recipe_list_view(request):
    meal_type = request.GET.get('meal_type')
    diet_suitability = request.GET.get('diet_suitability')
    health_condition = request.GET.get('health_condition')
    total_cost = request.GET.get('total_cost')

    total_cost = float(total_cost) if total_cost else None
    # Fetch all meals
    meals = Meal.objects.all()

    # Apply filters
    if meal_type:
        meals = meals.filter(meal_type=meal_type)
    if diet_suitability:
        meals = meals.filter(diet_suitability=diet_suitability)
    if health_condition:
        meals = meals.filter(health_condition_suitability__name=health_condition)
    if total_cost:
        meals = meals.filter(total_cost__lte=total_cost)

    health_conditions = HealthConditions.objects.all()

    return render(request, 'demo/recipe_list.html', {
        'meals': meals,
        'health_conditions': health_conditions,
        'meal_type': meal_type,
        'diet_suitability': diet_suitability,
        'health_condition': health_condition,
        'total_cost': total_cost
    })


def recipe_detail_view(request, recipe_id):
    recipe = get_object_or_404(Meal, id=recipe_id)
    associated_health_conditions = recipe.health_condition_suitability.all()
    return render(request, 'demo/recipe_detail.html', {
        'recipe': recipe,
        'associated_health_conditions': associated_health_conditions
    })


from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings

def feedback_page(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            rating = form.cleaned_data['rating']

            # Save feedback to the database
            feedback = Feedback(name=name, email=email, message=message, rating=rating)
            feedback.save()

            # Send email (adjust settings.py to enable email sending)
            try:
                send_mail(
                    subject=f"Contact Us Form Submission from {name}",
                    message=f"Name: {name}\nEmail: {email}\nRating: {rating}\n\nMessage:\n{message}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['support@example.com'],  # Replace with your support email
                )
                return HttpResponse("Your message has been sent successfully. We'll get back to you shortly.")
            except Exception as e:
                return HttpResponse(f"Error: {e}")
    else:
        form = FeedbackForm()
    return render(request, 'demo/feedback.html', {'form': form})

def contact_us(request):
    """
    Handles the contact form submission.
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Send email (adjust settings.py to enable email sending)
        try:
            send_mail(
                subject=f"Contact Us Form Submission from {name}",
                message=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['support@example.com'],  # Replace with your support email
            )
            return HttpResponse("Your message has been sent successfully. We'll get back to you shortly.")
        except Exception as e:
            return HttpResponse(f"Error: {e}")
    else:
        return HttpResponse("Invalid request.")
    
def logout_view(request):
    logout(request)
    return redirect('login')
