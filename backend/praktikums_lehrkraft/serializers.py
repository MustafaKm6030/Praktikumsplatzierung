from rest_framework import serializers
from .models import PraktikumsLehrkraft, PLSubjectAvailability
from schools.serializers import SchoolListSerializer
from subjects.models import Subject, PraktikumType


class PLSubjectAvailabilitySerializer(serializers.ModelSerializer):
    """
    Serializer for PL Subject Availability matrix.
    Business Logic: Shows which subjects a PL can teach for specific Praktikum types.
    """
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    praktikum_type_name = serializers.CharField(source='praktikum_type.get_code_display', read_only=True)
    
    class Meta:
        model = PLSubjectAvailability
        fields = ['id', 'subject', 'subject_name', 'praktikum_type', 'praktikum_type_name', 'is_available']


class PLListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing PLs.
    Business Logic: Shows essential PL information for list views.
    """
    school_name = serializers.CharField(source='school.name', read_only=True)
    main_subject_name = serializers.CharField(source='main_subject.name', read_only=True)
    program_display = serializers.CharField(source='get_program_display', read_only=True)
    
    class Meta:
        model = PraktikumsLehrkraft
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone',
            'school', 'school_name', 'program', 'program_display',
            'main_subject', 'main_subject_name', 'is_available'
        ]


class PLDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed PL view.
    Business Logic: Shows complete PL information including relationships.
    """
    school_detail = SchoolListSerializer(source='school', read_only=True)
    main_subject_name = serializers.CharField(source='main_subject.name', read_only=True)
    program_display = serializers.CharField(source='get_program_display', read_only=True)
    subject_availabilities = PLSubjectAvailabilitySerializer(many=True, read_only=True)
    available_praktikum_types_display = serializers.SerializerMethodField()
    available_subjects_display = serializers.SerializerMethodField()
    
    class Meta:
        model = PraktikumsLehrkraft
        exclude = ['available_praktikum_types', 'available_subjects']
    
    def get_available_praktikum_types_display(self, obj):
        """Returns list of available praktikum types with display names."""
        return [
            {'id': pt.id, 'code': pt.code, 'name': pt.get_code_display()}
            for pt in obj.available_praktikum_types.all()
        ]
    
    def get_available_subjects_display(self, obj):
        """Returns list of available subjects with names."""
        return [
            {'id': s.id, 'code': s.code, 'name': s.name}
            for s in obj.available_subjects.all()
        ]


class PLCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating PLs.
    Business Logic: Validates PL data and handles relationships.
    """
    
    class Meta:
        model = PraktikumsLehrkraft
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'school', 'program', 'main_subject',
            'available_praktikum_types', 'schulamt',
            'max_students_per_praktikum', 'max_simultaneous_praktikum',
            'besonderheiten', 'is_available', 'notes'
        ]
        extra_kwargs = {
            'phone': {'required': False},
            'main_subject': {'required': False, 'allow_null': True},
            'available_praktikum_types': {'required': False},
            'schulamt': {'required': False},
            'max_students_per_praktikum': {'required': False},
            'max_simultaneous_praktikum': {'required': False},
            'besonderheiten': {'required': False},
            'is_available': {'required': False},
            'notes': {'required': False},
        }
    
    def validate_email(self, value):
        """Validates email uniqueness."""
        instance = self.instance
        if instance:
            if PraktikumsLehrkraft.objects.exclude(pk=instance.pk).filter(email=value).exists():
                raise serializers.ValidationError("Email already exists.")
        else:
            if PraktikumsLehrkraft.objects.filter(email=value).exists():
                raise serializers.ValidationError("Email already exists.")
        return value
    
    def validate_max_simultaneous_praktikum(self, value):
        """Validates max simultaneous praktikum does not exceed 2."""
        if value and value > 2:
            raise serializers.ValidationError("Max simultaneous praktikum cannot exceed 2.")
        return value

