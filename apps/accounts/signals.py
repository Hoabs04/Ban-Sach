from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User


@receiver(post_save, sender=User)
def create_user_defaults(sender, instance, created, **kwargs):
    """Set up defaults when a new user is created."""
    if created and not instance.is_superuser:
        # Set default role for new users
        if not instance.role:
            instance.role = User.Role.CUSTOMER
            instance.save(update_fields=['role'])
