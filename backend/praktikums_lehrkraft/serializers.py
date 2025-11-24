from rest_framework import serializers
from .models import PraktikumsLehrkraft
from schools.serializers import SchoolListSerializer
from subjects.models import Subject, PraktikumType


class PLListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing PLs.
    Business Logic: Shows essential PL information for list views.
    """

    capacity = serializers.ReadOnlyField()
    school_name = serializers.CharField(source="school.name", read_only=True)
    program_display = serializers.CharField(
        source="get_program_display", read_only=True
    )
    main_subject_name = serializers.CharField(
        source="main_subject.name", read_only=True, allow_null=True
    )

    class Meta:
        model = PraktikumsLehrkraft
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "school",
            "school_name",
            "program",
            "program_display",
            "anrechnungsstunden",
            "schulamt",
            "capacity",
            "is_active",
            "main_subject",
            "available_subjects",
            "main_subject_name",
            "preferred_praktika_raw",
        ]


class PLDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed PL view.
    Business Logic: Shows complete PL information including relationships.
    """

    school_detail = SchoolListSerializer(source="school", read_only=True)
    main_subject_name = serializers.CharField(
        source="main_subject.name", read_only=True
    )
    program_display = serializers.CharField(
        source="get_program_display", read_only=True
    )
    available_praktikum_types_display = serializers.SerializerMethodField()
    available_subjects_display = serializers.SerializerMethodField()

    class Meta:
        model = PraktikumsLehrkraft
        fields = "__all__"

    def get_available_praktikum_types_display(self, obj):
        """Returns list of available praktikum types with display names."""
        return [
            {"id": pt.id, "code": pt.code, "name": pt.get_code_display()}
            for pt in obj.available_praktikum_types.all()
        ]

    def get_available_subjects_display(self, obj):
        """Returns list of available subjects with names."""
        return [
            {"id": s.id, "code": s.code, "name": s.name}
            for s in obj.available_subjects.all()
        ]


class PLCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating PLs.
    Business Logic: Validates PL data and handles relationships.
    """

    capacity = serializers.ReadOnlyField()
    main_subject_name = serializers.CharField(
        source="main_subject.name", read_only=True
    )

    class Meta:
        model = PraktikumsLehrkraft
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "school",
            "program",
            "main_subject",
            "available_praktikum_types",
            "preferred_praktika_raw",
            "schulamt",
            "anrechnungsstunden",
            "current_year_notes",
            "is_active",
            "notes",
            "available_subjects",
            "capacity",
            "main_subject_name",
        ]
        extra_kwargs = {
            "email": {"required": False, "allow_blank": True},
            "phone": {"required": False},
            "main_subject": {"required": False, "allow_null": True},
            "available_praktikum_types": {"required": False},
            "available_subjects": {"required": False},
            "schulamt": {"required": False},
            "anrechnungsstunden": {"required": False},
            "current_year_notes": {"required": False},
            "is_active": {"required": False},
            "notes": {"required": False},
        }

    def validate_email(self, value):
        """Validates email uniqueness."""
        if not value:
            return value
        instance = self.instance
        if instance:
            if (
                PraktikumsLehrkraft.objects.exclude(pk=instance.pk)
                .filter(email=value)
                .exists()
            ):
                raise serializers.ValidationError("Email already exists.")
        else:
            if PraktikumsLehrkraft.objects.filter(email=value).exists():
                raise serializers.ValidationError("Email already exists.")
        return value
