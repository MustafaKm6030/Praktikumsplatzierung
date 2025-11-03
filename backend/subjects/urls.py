from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubjectViewSet, PraktikumTypeViewSet

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'praktikum-types', PraktikumTypeViewSet, basename='praktikumtype')

urlpatterns = router.urls

