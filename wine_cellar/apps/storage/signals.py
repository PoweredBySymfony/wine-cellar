from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _

from wine_cellar.apps.storage.models import Storage


@receiver(post_save, sender=User)
def create_storage(sender, instance, created, **kwargs):
    if created:
        Storage.objects.create(
            name=_("Default Shelf"),
            user=instance,
            description=_("Default storage for wines"),
            location=_("Cellar"),
            rows=0,
            columns=0,
        )
