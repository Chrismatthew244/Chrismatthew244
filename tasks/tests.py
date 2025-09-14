from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.core.management import call_command
from .models import Customer, Task


class TaskModelTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name='Acme')

    def test_task_customer_relationship(self):
        task = Task.objects.create(
            customer=self.customer,
            title='Test Task',
            description='A task',
            deadline=timezone.now() + timedelta(days=1),
        )
        self.assertEqual(task.customer, self.customer)

    def test_mark_overdue_command(self):
        task = Task.objects.create(
            customer=self.customer,
            title='Past Task',
            description='Past due',
            deadline=timezone.now() - timedelta(days=1),
        )
        # Signal should set status to overdue
        self.assertEqual(task.status, Task.Status.OVERDUE)
        # Reset to pending and run management command
        task.status = Task.Status.PENDING
        task.save()
        call_command('mark_overdue_tasks')
        task.refresh_from_db()
        self.assertEqual(task.status, Task.Status.OVERDUE)
