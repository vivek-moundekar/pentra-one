from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages

def login_page(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect("dashboard")

        else:

            messages.error(
                request,
                "Invalid username or password."
            )

    return render(
        request,
        "account/login.html"
    )

def signup_page(request):

    if request.method == 'POST':

        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # Check required fields
        if not name or not email or not password:
            return render(request, 'account/signup.html', {
                'error': 'Please fill all the fields.'
            })

        # Check passwords
        if password != confirm_password:
            return render(request, 'account/signup.html', {
                'error': 'Passwords do not match.'
            })

        # Check existing email
        if User.objects.filter(email=email).exists():
            return render(request, 'account/signup.html', {
                'error': 'This email is already registered.'
            })

        # Create unique username
        username = email.split('@')[0]

        base_username = username
        counter = 1

        while User.objects.filter(username=username).exists():
            username = base_username + str(counter)
            counter += 1

        # Create user
        user = User.objects.create_user(
            username=username,
            first_name=name,
            email=email,
            password=password
        )

        # Login user
        login(
        request,
        user,
        backend='django.contrib.auth.backends.ModelBackend'
        )

        # Redirect to dashboard
        return redirect('/dashboard/')

    return render(request, 'account/signup.html')

def logout_user(request):
    logout(request)
    return redirect("home")