from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from movies.models import UserProfile

class Command(BaseCommand):
    help = 'Create UserProfile for all existing users'

    def handle(self, *args, **options):
        for user in User.objects.all():
            UserProfile.objects.get_or_create(user=user)
            self.stdout.write(
                self.style.SUCCESS(f'Created profile for {user.username}')
            )