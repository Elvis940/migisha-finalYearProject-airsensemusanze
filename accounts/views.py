from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.http import JsonResponse

from airsense_project.settings import DEFAULT_FROM_EMAIL
from .models import CustomUser
from .forms import CustomUserForm
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
import json
from .models import SensorData

@csrf_exempt
def receive_sensor_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            aqi = data.get('aqi')
            temperature = data.get('temperature')
            humidity = data.get('humidity')

            SensorData.objects.create(
                aqi=aqi,
                temperature=temperature,
                humidity=humidity
            )

            return JsonResponse({'message': 'Data saved successfully!'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=405)

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Hardcoded admin credentials
        if username == 'Elvis' and password == 'Godiswilling231@':
            # Create or get the admin user
            admin_user, created = CustomUser.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': 'Elvis',
                    'last_name': 'Harmon',
                    'email': 'elvis@example.com',
                    'role': 'admin',
                    'status': 'active',
                    'is_staff': True,
                    'is_superuser': True
                }
            )
            if created:
                admin_user.set_password(password)
                admin_user.save()
            
            # Log in the user
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Admin goes to admin dashboard
        else:
            # Regular user authentication
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.status == 'active':
                    login(request, user)
                    if user.role == 'admin':
                        return redirect('dashboard')  # Admin dashboard
                    else:
                        return redirect('user_dashboard')  # Regular user dashboard
                else:
                    messages.error(request, "Your account is not active yet. Please contact admin.")
            else:
                messages.error(request, "Invalid credentials.")
    
    return render(request, 'accounts/login.html')
def user_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Only allow active users to access the dashboard
    if request.user.status != 'active':
        logout(request)
        return redirect('login')
    
    # You can add any context data needed for the user dashboard here
    return render(request, 'accounts/user_dashboard.html')

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    users = CustomUser.objects.exclude(id=request.user.id)
    return render(request, 'accounts/dashboard.html', {'users': users})

def logout_view(request):
    logout(request)
    return redirect('login')

def get_user_data(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    data = {
        'username': user.username,  # Add this line
        'first_name': user.first_name,
        'last_name': user.last_name,
        'dob': user.dob.strftime('%Y-%m-%d') if user.dob else '',
        'phone_number': user.phone_number,
        'email': user.email,
        'role': user.role,
        'status': user.status,
    }
    return JsonResponse(data)

@csrf_exempt
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        try:
            form = CustomUserForm(request.POST, instance=user)
            
            if form.is_valid():
                # Only update password if it was provided
                if 'password' in form.cleaned_data and form.cleaned_data['password']:
                    user.set_password(form.cleaned_data['password'])
                user = form.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'User updated successfully!',
                    'user': {
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'dob': user.dob.strftime('%Y-%m-%d') if user.dob else '',
                        'phone_number': user.phone_number,
                        'email': user.email,
                        'role': user.role,
                        'status': user.status,
                    }
                })
            
            return JsonResponse({
                'success': False,
                'errors': form.errors.get_json_data(),
                'message': 'Form validation failed'
            }, status=400)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e),
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        user.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@csrf_exempt
def toggle_user_status(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        try:
            # New status flow logic
            if user.status == 'pending':
                user.status = 'active'  # First activation
            elif user.status == 'active':
                user.status = 'denied'  # Deny access
            elif user.status == 'denied':
                user.status = 'active'  # Re-activate
            else:
                user.status = 'pending'  # Fallback
            
            user.save()
            return JsonResponse({
                'success': True,
                'new_status': user.status,
                'button_text': 'Deny' if user.status == 'active' else 'Grant'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)

@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        try:
            data = request.POST.dict()
            data['status'] = 'pending'
            
            form = CustomUserForm(data)
            if not form.is_valid():
                return JsonResponse({
                    'success': False,
                    'errors': form.errors.get_json_data()
                }, status=400)
            
            user = form.save(commit=False)
            password = form.cleaned_data.get('password')
            user.set_password(password)
            user.save()
            
            # Send welcome email with credentials
            try:
                subject = 'Your AirSense Musanze Account'
                context = {
                    'user': user,
                    'username': user.username,
                    'password': password,
                    'login_url': request.build_absolute_uri('/accounts/login/')
                }
                
                # Text version
                text_content = f"""
                Welcome {user.first_name},

                Your AirSense Musanze account has been created successfully!

                Here are your login credentials:
                Username: {user.username}
                Password: {password}

                You can now login at: {context['login_url']}

                Thank you,
                AirSense Musanze Team
                """
                
                # HTML version
                html_content = render_to_string('accounts/email/welcome_email.html', context)
                
                msg = EmailMultiAlternatives(
                    subject,
                    text_content,
                    DEFAULT_FROM_EMAIL,
                    [user.email],
                    reply_to=[DEFAULT_FROM_EMAIL],
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send(fail_silently=False)
                
            except Exception as e:
                print(f"Failed to send email: {str(e)}")
                # You might want to log this error in production
                return JsonResponse({
                    'success': True,
                    'message': 'User registered but email failed to send'
                })
            
            return JsonResponse({
                'success': True,
                'message': 'User registered successfully!'
            })
            
        except Exception as e:
            print(f"Registration error: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'Registration failed'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)
