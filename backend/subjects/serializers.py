from rest_framework import serializers
from .models import Subject, PraktikumType


class SubjectSerializer(serializers.ModelSerializer):
    """Serializer for Subject model."""
    
    class Meta:
        model = Subject
        fields = '__all__'


class PraktikumTypeSerializer(serializers.ModelSerializer):
    """Serializer for PraktikumType model."""
    
    class Meta:
        model = PraktikumType
        fields = '__all__'

