from django.core.management.base import BaseCommand
from django.utils import timezone
from tasks.models import Task


class Command(BaseCommand):
    help = 'Mark tasks with past deadlines as overdue'

    def handle(self, *args, **options):
        now = timezone.now()
        updated = Task.objects.filter(
            deadline__lt=now,
            status=Task.Status.PENDING,
        ).update(status=Task.Status.OVERDUE)
        self.stdout.write(f'Updated {updated} tasks to overdue')
