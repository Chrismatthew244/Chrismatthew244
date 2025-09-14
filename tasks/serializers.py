from rest_framework import serializers
from .models import Customer, Task


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name']


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'customer', 'title', 'description', 'status', 'deadline']
