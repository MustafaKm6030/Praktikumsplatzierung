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
    available_praktikum_types_display = serializers.SerializerMethodField()

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
            "available_praktikum_types",
            "available_praktikum_types_display",
            "main_subject_name",
            "preferred_praktika_raw",
        ]

    def get_available_praktikum_types_display(self, obj):
        """Returns list of available praktikum types with display names."""
        return [
            {"id": pt.id, "code": pt.code, "name": pt.get_code_display()}
            for pt in obj.available_praktikum_types.all()
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
                raise serializers.ValidationError("E-Mail existiert bereits.")
        else:
            if PraktikumsLehrkraft.objects.filter(email=value).exists():
                raise serializers.ValidationError("E-Mail existiert bereits.")
        return value

    def _parse_praktikum_types_from_raw(self, preferred_praktika_raw):
        """Parses preferred_praktika_raw and returns list of PraktikumType objects."""
        if not preferred_praktika_raw:
            return []
        
        pref_raw_upper = preferred_praktika_raw.upper()
        all_praktikum_types = PraktikumType.objects.all()
        
        ptypes = []
        for ptype in all_praktikum_types:
            code_normalized = ptype.code.replace("_", " ")
            if code_normalized in pref_raw_upper:
                ptypes.append(ptype)
        
        return ptypes

    def create(self, validated_data):
        """Creates a new PL and parses preferred_praktika_raw if needed."""
        preferred_praktika_raw = validated_data.pop('preferred_praktika_raw', '')
        available_praktikum_types = validated_data.pop('available_praktikum_types', None)
        available_subjects = validated_data.pop('available_subjects', None)
        
        instance = PraktikumsLehrkraft.objects.create(
            preferred_praktika_raw=preferred_praktika_raw,
            **validated_data
        )
        
        if available_praktikum_types is not None:
            type_ids = []
            if not isinstance(available_praktikum_types, list):
                available_praktikum_types = [available_praktikum_types]
            for item in available_praktikum_types:
                if isinstance(item, PraktikumType):
                    type_ids.append(item.id)
                elif isinstance(item, (int, str)):
                    type_ids.append(int(item))
            instance.available_praktikum_types.set(type_ids)
        elif preferred_praktika_raw:
            parsed_types = self._parse_praktikum_types_from_raw(preferred_praktika_raw)
            instance.available_praktikum_types.set(parsed_types)
        
        if available_subjects is not None:
            from subjects.models import Subject
            subject_ids = []
            if not isinstance(available_subjects, list):
                available_subjects = [available_subjects]
            for item in available_subjects:
                if isinstance(item, Subject):
                    subject_ids.append(item.id)
                elif isinstance(item, (int, str)):
                    subject_ids.append(int(item))
            instance.available_subjects.set(subject_ids)
        
        return instance

    def update(self, instance, validated_data):
        """Updates PL and parses preferred_praktika_raw if needed."""
        preferred_praktika_raw = validated_data.pop('preferred_praktika_raw', None)
        available_praktikum_types = validated_data.pop('available_praktikum_types', None)
        available_subjects = validated_data.pop('available_subjects', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        if available_praktikum_types is not None:
            type_ids = []
            if not isinstance(available_praktikum_types, list):
                available_praktikum_types = [available_praktikum_types]
            for item in available_praktikum_types:
                if isinstance(item, PraktikumType):
                    type_ids.append(item.id)
                elif isinstance(item, (int, str)):
                    type_ids.append(int(item))
            instance.available_praktikum_types.set(type_ids)
        elif preferred_praktika_raw is not None:
            instance.preferred_praktika_raw = preferred_praktika_raw
            parsed_types = self._parse_praktikum_types_from_raw(preferred_praktika_raw)
            instance.available_praktikum_types.set(parsed_types)
            instance.save()
        
        if available_subjects is not None:
            from subjects.models import Subject
            subject_ids = []
            if not isinstance(available_subjects, list):
                available_subjects = [available_subjects]
            for item in available_subjects:
                if isinstance(item, Subject):
                    subject_ids.append(item.id)
                elif isinstance(item, (int, str)):
                    subject_ids.append(int(item))
            instance.available_subjects.set(subject_ids)
        
        return instance
