from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Subject, PraktikumType
from .serializers import SubjectSerializer, PraktikumTypeSerializer


class SubjectViewSet(viewsets.ModelViewSet):
    """
    API endpoints for Subject management.
    
    list: Get all subjects
    retrieve: Get a specific subject
    create: Create a new subject
    update: Update a subject
    destroy: Delete a subject
    """
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    # permission_classes = [IsAuthenticated]  # Uncomment when auth is ready


class PraktikumTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoints for Praktikum Type management.
    
    list: Get all praktikum types
    retrieve: Get a specific praktikum type
    create: Create a new praktikum type
    update: Update a praktikum type
    destroy: Delete a praktikum type
    """
    queryset = PraktikumType.objects.all()
    serializer_class = PraktikumTypeSerializer
    # permission_classes = [IsAuthenticated]
