from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from tasks.views import CustomerViewSet, TaskViewSet

router = DefaultRouter()
router.register(r'customers', CustomerViewSet)
router.register(r'tasks', TaskViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
