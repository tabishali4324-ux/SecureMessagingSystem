from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile, RegistrationRequest
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.hashers import make_password

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

        pending_exist = RegistrationRequest.objects.filter(username=username, status="PENDING").first()

        if pending_exist:
            messages.error(request,"A request for this username is already pending")
            return render(request, 'accounts/signup.html')


        new_request = RegistrationRequest(username=username,password=make_password(password), age=age)
        new_request.save()

        return render(request, "accounts/signup.html", {'submitted_username': username})

    return render(request, 'accounts/signup.html')

def registration_status(request, username):
    req = RegistrationRequest.objects.filter(username=username).first()
    status = req.status if req else "NOT_FOUND"
    return JsonResponse({"status": status})

def admin_verify(request):
    if not request.user.is_authenticated or request.user.profile.role != "admin":
        messages.error(request, "Access denied.")
        return redirect("login")

    if request.method == "POST":
        username = request.POST.get('username')
        action = request.POST.get("login")
        req = RegistrationRequest.objects.filter(username=username, status="PENDING").first()


        if req is None:
            messages.error(request, "Request not found or already handled.")
            return redirect("admin_verify")

        if action == "allow":
            new_user = User(username=req.username, password=req.password)
            new_user.save()
            Profile.objects.create(user=new_user, age=req.age, role="user")
            req.status = "APPROVED"
            req.save()
            messages.success(request, f"{req.username} approved.")
        elif action == "deny":
            req.status = "DENIED"
            req.save()
            messages.info(request,f"{req.username} denied.")

        return redirect("admin_verify")

    pending =RegistrationRequest.objects.filter(status="PENDING")
    return render(request, "accounts/admin_verify.html", {"pending": pending})

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