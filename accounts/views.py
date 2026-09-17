from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile
from django.contrib.auth import authenticate, login as auth_login

# Create your views here.

def signup(request):
    if request.method ==  "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        age= request.POST.get('age')

        if username == "" or password == "":
            messages.error(request, "Please fill all the fields")
            return render(request, 'accounts/signup.html')

        user_exist = User.objects.filter(username=username).first()

        if user_exist:
            messages.error(request, "Username is already taken")
            return render(request,'accounts/signup.html')

        new_user = User.objects.create_user(username=username,password=password)
        new_user.save()

        new_profile = Profile(user=new_user , age=age)
        new_profile.save()

        messages.success(request, "Account created, please login now")
        return redirect('login')

    return render(request, 'accounts/signup.html')

def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username == "" or password == "":
            messages.error(request, "Please Fill all the fields")
            return render(request, 'accounts/login.html')

        user= authenticate(request,username=username, password=password)

        if user is None:
            messages.error(request, "Invalid username or password")
            return render (request, 'accounts/login.html')

        auth_login(request, user)
        return redirect("home")

    return render(request, 'accounts/login.html')

def home(request):
    return render(request, "accounts/home.html")