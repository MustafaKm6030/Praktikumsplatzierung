from rest_framework import serializers
from .models import School


class SchoolListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = School
        fields = ['id', 'name', 'school_type', 'district', 'opnv_zone', 'is_active']


class SchoolDetailSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = School
        fields = '__all__'


class SchoolImportSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = School
        fields = '__all__'
        extra_kwargs = {
            'latitude': {'required': False},
            'longitude': {'required': False},
            'contact_person': {'required': False},
            'phone': {'required': False},
            'email': {'required': False},
            'notes': {'required': False},
        }

