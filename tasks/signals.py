from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Task


@receiver(pre_save, sender=Task)
def set_overdue_status(sender, instance, **kwargs):
    if instance.deadline and instance.status != Task.Status.COMPLETED:
        if instance.deadline < timezone.now():
            instance.status = Task.Status.OVERDUE
