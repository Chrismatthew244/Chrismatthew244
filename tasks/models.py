from django.db import models
from django.utils import timezone


class Customer(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Task(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'
        OVERDUE = 'overdue', 'Overdue'

    customer = models.ForeignKey(Customer, related_name='tasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    deadline = models.DateTimeField()

    def mark_overdue(self):
        if self.status != self.Status.COMPLETED and self.deadline < timezone.now():
            self.status = self.Status.OVERDUE
            self.save(update_fields=['status'])

    def __str__(self):
        return self.title
