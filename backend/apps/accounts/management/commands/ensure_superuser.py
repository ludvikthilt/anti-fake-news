import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from apps.accounts.models import Role


class Command(BaseCommand):
    help = "Create or promote the configured deployment administrator."

    def handle(self, *args, **options):
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "")
        if not email or not password:
            raise CommandError("DJANGO_SUPERUSER_EMAIL and DJANGO_SUPERUSER_PASSWORD are required.")

        User = get_user_model()
        matches = User.objects.filter(email__iexact=email)
        if matches.count() > 1:
            raise CommandError(f"More than one account matches {email!r}.")

        user = matches.first()
        if user is None:
            User.objects.create_superuser(email=email, password=password)
            self.stdout.write(f"Created administrator account {email}.")
            return

        fields_to_update = []
        if not user.is_superuser:
            user.is_superuser = True
            fields_to_update.append("is_superuser")
        if not user.check_password(password):
            user.set_password(password)
            fields_to_update.append("password")
        for field, value in (
            ("is_staff", True),
            ("is_active", True),
            ("is_email_verified", True),
            ("role", Role.ADMIN),
        ):
            if getattr(user, field) != value:
                setattr(user, field, value)
                fields_to_update.append(field)

        if fields_to_update:
            user.save(update_fields=fields_to_update)
            self.stdout.write(f"Promoted {email} to administrator.")
        else:
            self.stdout.write(f"Administrator account {email} already exists.")
