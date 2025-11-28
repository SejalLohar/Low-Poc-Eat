# demo/utils.py
import random
from django.core.mail import send_mail
from django.conf import settings

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(user, otp):
    subject = 'Your OTP for Email Verification'
    message = f'Your OTP is {otp}. Please use this to verify your email.'
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    send_mail(subject, message, email_from, recipient_list)
