from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import *

# Create your views here.


def home(request):
    return render(request,"index.html")

def login_view(request):
    show = 'signin'   # default form

    if request.method == 'POST':
        action = request.POST.get('action')

        # ---------- SIGNIN ----------
        if action == 'signin':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)

            if user:
                login(request, user)
                return redirect('home')
            else:
                return render(request, 'signin.html', {'info': 'Invalid username or password','show': 'signin'})

        # ----- CREATE NEW ACCOUNT -----
        if action == 'create':
            username = request.POST.get('username')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

            if password1 != password2:
                return render(request, 'signin.html', {'info': 'Passwords do not match','show': 'create'})

            if User.objects.filter(username=username).exists():
                return render(request, 'signin.html', {'info': 'Username already exists','show': 'create'})

            User.objects.create_user(username=username, password=password1)
            return render(request, 'signin.html', {'info': 'Account created successfully','show': 'signin'})

        # BUTTON CLICK (toggle only)
        if action == 'show_signin':
            show = 'signin'

        if action == 'show_create':
            show = 'create'

    return render(request, 'signin.html', {'show': show})


def course(request):
    return render(request, 'course.html')


def submit(request):
    return redirect("home")


def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        call_time = request.POST.get('call_time')
        enquiry = request.POST.get('enquiry')

        # For now just printing (later you can save to DB)
        print(name, phone, call_time, enquiry)

        return redirect('home')

    return render(request, 'contact.html')

