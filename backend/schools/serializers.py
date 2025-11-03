from rest_framework import serializers
from .models import School


class SchoolListSerializer(serializers.ModelSerializer):
    """Serializer for listing schools (minimal fields)."""
    
    class Meta:
        model = School
        fields = ['id', 'name', 'school_type', 'district', 'opnv_zone', 'is_active']


class SchoolDetailSerializer(serializers.ModelSerializer):
    """Serializer for school details (all fields)."""
    
    class Meta:
        model = School
        fields = '__all__'

