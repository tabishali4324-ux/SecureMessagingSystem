from django.core.management.base import BaseCommand
from django..contrib.auth.models import User
from accounts.models import Profile

class Command(BaseCommand):
    help = "Creates a default admin user if one doesn't already exist."

    def handle(self, *args, **options):
        username = "Humhai"
        password= "hojabhai333"

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"User '{username}' already exists. Skipping"))
            return

        user = User.objects.create_user(username=username, password=password)
        Profile.objects.create(user=user, role="admin")
        self.stdout.write(self.style.SUCCESS(f"Default admin'{username}' created."))