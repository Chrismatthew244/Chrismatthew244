from rest_framework import viewsets
from .models import Customer, Task
from .serializers import CustomerSerializer, TaskSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get('status')
        customer = self.request.query_params.get('customer')
        if status:
            queryset = queryset.filter(status=status)
        if customer:
            queryset = queryset.filter(customer_id=customer)
        return queryset
