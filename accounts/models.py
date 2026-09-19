from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField(null=True, blank=True)
    ROLE_CHOICES = [("user", "User"), ("admin", "Admin")]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="user")

    def __str__(self):
        return self.user.username

class RegistrationRequest(models.Model):
    username= models.CharField(max_length=50)
    password = models.CharField(max_length=200)
    age= models.IntegerField()
    status = models.CharField(max_length=10, default="PENDING")

    def __str__(self):
        return self.username

class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver=models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    encrypted_text =models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} @ {self.timestamp}"


    