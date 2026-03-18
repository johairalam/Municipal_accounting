from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Ensure default ROOT_DEV user exists"

    def handle(self, *args, **options):
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username="Johair",
            defaults={"email": "johair@example.com"},
        )
        user.set_password("Aalalm@123")  # default password
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.role = "ROOT_DEV"
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS("Created default ROOT_DEV user: Johair / Aalalm@123"))
        else:
            self.stdout.write(self.style.SUCCESS("Updated ROOT_DEV user: Johair / Aalalm@123"))
