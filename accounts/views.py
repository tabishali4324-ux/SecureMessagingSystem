from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile, RegistrationRequest, Message
from . import crypto
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.conf import settings


# Create your views here.

def signup(request):
    if request.method ==  "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        age= request.POST.get('age')

        if username == "" or password == "" or age == "":
            messages.error(request, "Please fill all the fields")
            return render(request, 'accounts/signup.html')

        if not age.isdigit() or int(age) <= 0 or int(age) > 120:
            messages.error(request, "Age must be a valid number")
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

@login_required
def logout_view(request):
    auth_logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("login")

def admin_verify(request):
    if not request.user.is_authenticated or request.user.profile.role != "admin":
        messages.error(request, "Access denied.")
        return redirect("login")

    if request.method == "POST":
        username = request.POST.get('username')
        action = request.POST.get("action")
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
        else:
            messages.error(request,"Invalid Action")

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
            pending = RegistrationRequest.objects.filter(username=username, status="PENDING").first()
            if pending:
                messages.error(request,"Your accpunt is still waiting for approval ")
            else:
                messages.error(request, "Invalid username or password")
            return render (request, 'accounts/login.html')

        auth_login(request, user)
        return redirect("home")

    return render(request, 'accounts/login.html')

@login_required
def home(request):
    return render(request, "accounts/home.html")

@login_required
def user_list(request):
    users = User.objects.exclude(pk=request.user.pk).exclude(profile__role="admin").exclude(is_superuser=True)
    return render(request, "accounts/user_list.html", {"users":users})

@login_required
def send_messages(request, username):
    receiver = User.objects.filter(username=username).exclude(profile__role='admin').exclude(is_superuser=True).first()
    if receiver is None:
        messages.error(request, "user not found")
        return redirect("user_list")

    if request.method == "POST":
        text = request.POST.get("message")
        if text:
            encrypted = crypto.encrypt_message(text, settings.MESSAGE_VAULT_PASSWORD)
            Message.objects.create(sender=request.user, receiver=receiver, encrypted_text=encrypted)
            messages.success(request, "Message sent.")
        else:
            messages.error(request, "Message cannot be empty")
        return redirect("send_message", username=username)

    return render(request,"accounts/send_message.html", {"receiver": receiver})

@login_required
def inbox(request):
    inbox_messages = []
    for m in Message.objects.filter(receiver=request.user).order_by("timestamp"):
        try:
            text = crypto.decrypt_message(m.encrypted_text, settings.MESSAGE_VAULT_PASSWORD)
        except Exception:
            text = "[Unable to decrypt]"
        inbox_messages.append({"sender": m.sender.username, "text":text, "timestamp": m.timestamp})


    return render(request, "accounts/inbox.html", {"inbox_messages":inbox_messages})

@login_required
def admin_check_messages(request):
    if request.user.profile.role != "admin":
        messages.error(request, "Access denied.")
        return redirect("login")

    users = User.objects.exclude(profile__role="admin").exclude(is_superuser=True).order_by("username")

    conversation = None 
    user1 = request.GET.get("user1")
    user2 = request.GET.get("user2")

    if user1 and user2 and user1 != user2:
        conversation = Message.objects.filter(
            sender__username=user1, receiver__username=user2

        ) | Message.objects.filter(
            sender__username=user2, receiver__username=user1
        )
        conversation = conversation.order_by("timestamp")
    elif user1 and user2 and user1 == user2:
        messages.error(request,"Please select two different users")

    return render(request, "accounts/admin_check_messages.html", {
        "users": users, "conversation": conversation, "user1": user1, "user2":user2,

    }) 


@login_required
def admin_decrypt_messages(request):
    if request.user.profile.role != "admin":
        messages.error(request, "Access denied.")
        return redirect("login")

    user1 = request.GET.get("user1") or request.POST.get("user1")
    user2 = request.GET.get("user2") or request.POST.get("user2")

    if not user1 or not user2:
        messages.error(request, "Please select two users first.")
        return redirect("admin_check_messages")

    decrypted = None
    error = None

    if request.method == "POST":
        password = request.POST.get("password")
        if password != settings.MESSAGE_VAULT_PASSWORD:
            error = "Incorrect decryption password."
        else:
            convo = Message.objects.filter(
                sender__username=user1, receiver__username=user2
            ) | Message.objects.filter(
                sender__username=user2, receiver__username=user1
            )
            decrypted = []
            try:
                for m in convo.order_by("timestamp"):
                    text = crypto.decrypt_message(m.encrypted_text, password)
                    decrypted.append({
                        "sender": m.sender.username,
                        "receiver": m.receiver.username,
                        "text": text,
                        "timestamp": m.timestamp,
                    })
            except Exception:
                error = "Unable to decrypt messages."
                decrypted = None

    return render(request, "accounts/admin_decrypt.html", {
        "user1": user1, "user2": user2, "decrypted": decrypted, "error": error,
    })

@login_required
def admin_remove_users(request):
    if request.user.profile.role != "admin":
        messages.error(request, "Access denied.")
        return redirect("login")

    status = None

    if request.method == "POST":
        username = request.POST.get('username')
        user_to_remove = User.objects.filter(username=username).exclude(profile__role="admin").exclude(is_superuser=True).first()
        if not user_to_remove:
            messages.error(request, "Select a valid user")
        else:
            user_to_remove.delete()
            messages.success(request, "User removed successfully")
            status = "User removed suceessfully"

    users = User.objects.exclude(profile__role="admin").exclude(is_superuser=True).order_by("username")
    return render(request, "accounts/admin_remove_users.html", {"users": users, "status": status})
