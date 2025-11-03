from rest_framework import serializers
from .models import Student, StudentPraktikumPreference
from subjects.models import Subject


class StudentListSerializer(serializers.ModelSerializer):
    primary_subject_name = serializers.CharField(source='primary_subject.name', read_only=True)
    
    class Meta:
        model = Student
        fields = ['id', 'student_id', 'first_name', 'last_name', 'email', 'program', 'primary_subject_name']


class StudentDetailSerializer(serializers.ModelSerializer):
    primary_subject_name = serializers.CharField(source='primary_subject.name', read_only=True)
    additional_subjects_names = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = '__all__'
    
    def get_additional_subjects_names(self, obj):
        return [subject.name for subject in obj.additional_subjects.all()]


class StudentImportSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Student
        fields = '__all__'
        extra_kwargs = {
            'phone': {'required': False},
            'major': {'required': False},
            'enrollment_date': {'required': False},
            'primary_subject': {'required': False},
            'home_address': {'required': False},
            'home_region': {'required': False},
            'preferred_zone': {'required': False},
            'notes': {'required': False},
        }


class StudentPraktikumPreferenceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = StudentPraktikumPreference
        fields = '__all__'

