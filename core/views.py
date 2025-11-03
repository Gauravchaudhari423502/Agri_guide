from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.conf import settings
import json
from .gemini_api import get_agriculture_response, get_crop_recommendation
from .translation_service import translation_service

def welcome_view(request):
    return render(request, 'core/welcome.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Account created for {username}!")
            login(request, user)
            return redirect('dashboard')
        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")
    else:
        form = UserCreationForm()
    return render(request, 'core/register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('welcome')

@login_required
def dashboard_view(request):
    return render(request, 'core/dashboard.html')

@login_required
def chatbot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            language = data.get('language', 'en')
            
            if not user_message:
                return JsonResponse({'error': 'No message provided'}, status=400)
            
            # Get response from Gemini API
            response = get_agriculture_response(user_message, language)
            
            return JsonResponse({'response': response})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

@login_required
def crop_prediction_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Extract soil and weather data
            soil_data = {
                'nitrogen': data.get('nitrogen'),
                'phosphorus': data.get('phosphorus'),
                'potassium': data.get('potassium'),
                'temperature': data.get('temperature'),
                'humidity': data.get('humidity'),
                'ph': data.get('ph'),
                'rainfall': data.get('rainfall')
            }
            
            # Get crop recommendation
            recommendation = get_crop_recommendation(soil_data)
            
            return JsonResponse(recommendation)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

def superuser_login_view(request):
    """Special login view for superuser with predefined credentials"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Check if it's the superuser login
        if username == 'admin' and password == 'admin123':
            try:
                user = User.objects.get(username='admin')
                if user.is_superuser:
                    login(request, user)
                    messages.success(request, "Superuser login successful!")
                    return redirect('dashboard')
                else:
                    messages.error(request, "User is not a superuser.")
            except User.DoesNotExist:
                messages.error(request, "Superuser does not exist. Please create one first.")
        else:
            messages.error(request, "Invalid superuser credentials.")
    else:
        # Check if superuser exists, if not create one
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@agriguide.com', 'admin123')
            messages.info(request, "Superuser created with username: admin, password: admin123")
    
    return render(request, 'core/superuser_login.html')

@login_required
def translation_api(request):
    """API endpoint for text translation"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text', '')
            target_language = data.get('target_language', 'en')
            source_language = data.get('source_language', 'auto')
            
            if not text:
                return JsonResponse({'error': 'No text provided'}, status=400)
            
            # Translate the text
            result = translation_service.translate_text(
                text, 
                target_language=target_language,
                source_language=source_language
            )
            
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

def get_supported_languages_api(request):
    """API endpoint to get supported languages"""
    try:
        languages = translation_service.get_supported_languages()
        return JsonResponse({'languages': languages})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def database_view(request):
    """Database access view for superusers only"""
    if not request.user.is_superuser:
        messages.error(request, "Access denied. Superuser privileges required.")
        return redirect('dashboard')
    
    # Get database information
    from django.db import connection
    from django.contrib.auth.models import User
    import os
    
    # Get database path
    db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
    db_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
    
    # Get user statistics
    total_users = User.objects.count()
    superusers = User.objects.filter(is_superuser=True).count()
    staff_users = User.objects.filter(is_staff=True).count()
    active_users = User.objects.filter(is_active=True).count()
    
    # Get recent users
    recent_users = User.objects.order_by('-date_joined')[:10]
    
    context = {
        'db_path': db_path,
        'db_size': db_size,
        'total_users': total_users,
        'superusers': superusers,
        'staff_users': staff_users,
        'active_users': active_users,
        'recent_users': recent_users,
    }
    
    return render(request, 'core/database.html', context)
