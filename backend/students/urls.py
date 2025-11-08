from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, StudentPraktikumPreferenceViewSet

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')
router.register(r'student-preferences', StudentPraktikumPreferenceViewSet, basename='studentpreference')

urlpatterns = router.urls

