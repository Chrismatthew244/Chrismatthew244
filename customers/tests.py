from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Customer


class CustomerAPITestCase(APITestCase):
    def setUp(self):
        self.list_url = reverse('customer-list')

    def test_create_customer(self):
        data = {'name': 'Test', 'contact_info': 'test@example.com', 'status': 'active'}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(Customer.objects.get().name, 'Test')

    def test_read_customer(self):
        customer = Customer.objects.create(name='Test', contact_info='test@example.com', status='active')
        url = reverse('customer-detail', args=[customer.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test')

    def test_update_customer(self):
        customer = Customer.objects.create(name='Test', contact_info='test@example.com', status='active')
        url = reverse('customer-detail', args=[customer.id])
        data = {'name': 'New Name', 'contact_info': 'new@example.com', 'status': 'inactive'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        customer.refresh_from_db()
        self.assertEqual(customer.name, 'New Name')

    def test_delete_customer(self):
        customer = Customer.objects.create(name='Test', contact_info='test@example.com', status='active')
        url = reverse('customer-detail', args=[customer.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Customer.objects.count(), 0)
