from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm
from .models import Profile,OTP,User
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import datetime
import random

def signup_view(request):
    """Handle user registration."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = False 
            user.save()
            
            otp_code = generate_otp()
            valid_until = timezone.now() + datetime.timedelta(minutes=5)
            OTP.objects.create(user=user, code=otp_code, valid_until=valid_until)
            send_otp_email(user, otp_code)
            
            # Redirect to OTP verification page
            return redirect('verify_otp', user_id=user.id)

        # If form not valid, re-render form with errors
        return render(request, 'users/register.html', {'form': form})
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})


 # Deactivate account until OTP verified
    

       

def login_view(request):
    """Handle user login."""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('user-profile', user_id=request.user.id)

        else:
            return render(request, 'users/login.html', {'error': 'Invalid credentials'})
    return render(request, 'users/login.html')

def logout_view(request):
    """Handle user logout."""
    logout(request)
    return redirect('lesson-list')

from django.shortcuts import get_object_or_404

@login_required
def profile_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile, created = Profile.objects.get_or_create(
        user=user,
        defaults={
            'full_name': user.get_full_name() or user.username,
            'grade': 'Not set',
            'school': 'Not set',
            'address': 'Not set',
            'gender': 'O',
            'dob': '2000-01-01',
        }
    )
    return render(request, 'users/profile.html', {
        'user': user,
        'profile': profile
    })
@login_required
def student_list_view(request):
    students = Profile.objects.select_related('user').all()
    return render(request, 'ai_engine/students_list.html', {'students': students})




def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(user, otp_code):
    subject = 'Your OTP Code'
    message = f'Your OTP code is {otp_code}'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list)

def request_otp(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        user = User.objects.filter(username=username).first()
        if user:
            otp_code = generate_otp()
            valid_until = timezone.now() + datetime.timedelta(minutes=5)
            OTP.objects.create(user=user, code=otp_code, valid_until=valid_until)
            send_otp_email(user, otp_code)
            return redirect('verify_otp', user_id=user.id)
        else:
            return render(request, 'users/request_otp.html', {'error': 'User not found'})
    return render(request, 'users/request_otp.html')

def verify_otp(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        otp_code = request.POST.get('otp')
        otp = OTP.objects.filter(user=user, code=otp_code).order_by('-created_at').first()
        if otp and otp.is_valid():
            user.is_active = True
            user.save()
            login(request, user)  # Log the user in immediately after verification
            return render(request, 'users/otp_success.html')
        else:
            return render(request, 'users/verify_otp.html', {'error': 'Invalid or expired OTP'})

    return render(request, 'users/verify_otp.html')
