from rest_framework import serializers
from .models import School


class SchoolListSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = [
            "id",
            "name",
            "school_type",
            "city",
            "district",
            "zone",
            "opnv_code",
            "is_active",
            "distance_km",
            "latitude",
            "longitude",
        ]


class SchoolDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = "__all__"


class SchoolImportSerializer(serializers.ModelSerializer):
    # This serializer is no longer needed, as import logic will be custom.
    # We keep it for potential future use but the primary import will be from the PL CSV.
    class Meta:
        model = School
        fields = [
            "name",
            "school_type",
            "city",
            "district",
            "zone",
            "opnv_code",
            "distance_km",
            "is_active",
            "notes",
            "latitude",
            "longitude",
        ]
