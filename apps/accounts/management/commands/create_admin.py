from django.core.management.base import BaseCommand
from apps.accounts.models import User


class Command(BaseCommand):
    help = 'Creates default admin manager user'

    def handle(self, *args, **options):
        u, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'Admin',
                'last_name': 'Manager',
                'is_staff': True,
                'is_superuser': True,
                'role': User.Role.OWNER,
                'phone_number': '012 345 678'
            }
        )
        u.set_password('admin123')
        u.is_staff = True
        u.is_superuser = True
        u.role = User.Role.OWNER
        u.save()
        self.stdout.write(self.style.SUCCESS("Admin user 'admin' (password: admin123) is ready!"))
