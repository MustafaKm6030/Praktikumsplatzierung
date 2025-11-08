from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PLViewSet

router = DefaultRouter()
router.register(r'', PLViewSet, basename='pl')

urlpatterns = router.urls

