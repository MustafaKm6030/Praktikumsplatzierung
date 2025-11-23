from rest_framework import serializers
from .models import Student
from subjects.models import Subject


class StudentListSerializer(serializers.ModelSerializer):
    primary_subject_name = serializers.CharField(
        source="primary_subject.name", read_only=True
    )

    class Meta:
        model = Student
        fields = [
            "id",
            "student_id",
            "first_name",
            "last_name",
            "email",
            "program",
            "primary_subject_name",
            "placement_status",
            "home_region",
        ]


class StudentDetailSerializer(serializers.ModelSerializer):
    primary_subject_name = serializers.CharField(
        source="primary_subject.name", read_only=True
    )

    class Meta:
        model = Student
        fields = "__all__"


class StudentCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating students.
    Includes all fields so they can be edited via API.
    """

    class Meta:
        model = Student
        fields = "__all__"


class StudentImportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = "__all__"
        extra_kwargs = {
            "phone": {"required": False},
            "major": {"required": False},
            "enrollment_date": {"required": False},
            "primary_subject": {"required": False},
            # Location Fields
            "home_address": {"required": False},
            "semester_address": {"required": False},  # Added new field
            "home_region": {"required": False},
            "preferred_zone": {"required": False},
            # Completion Checklist (Optional on import)
            "pdp1_completed_date": {"required": False},
            "pdp2_completed_date": {"required": False},
            "sfp_completed_date": {"required": False},
            "zsp_completed_date": {"required": False},
            "notes": {"required": False},
        }
