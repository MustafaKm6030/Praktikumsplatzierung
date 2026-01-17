from rest_framework import serializers
from .models import Assignment, StudentAssignment


class AssignmentSerializer(serializers.ModelSerializer):
    """Serializer for the Assignment model."""

    mentor_name = serializers.CharField(source="mentor.last_name", read_only=True)
    practicum_type_code = serializers.CharField(
        source="practicum_type.code", read_only=True
    )
    subject_code = serializers.CharField(
        source="subject.code", read_only=True, allow_null=True
    )
    school_name = serializers.CharField(source="school.name", read_only=True)

    class Meta:
        model = Assignment
        fields = [
            "id",
            "mentor",
            "mentor_name",
            "practicum_type_code",
            "subject_code",
            "school_name",
            "academic_year",
        ]


class DemandSerializer(serializers.Serializer):
    """
    Serializer for the aggregated demand data.
    This is not a ModelSerializer because the data is computed.
    """

    practicum_type = serializers.CharField()
    program_type = serializers.CharField()
    subject_code = serializers.CharField(allow_null=True)
    subject_display_name = serializers.CharField(allow_null=True)
    required_slots = serializers.IntegerField()


# ==================== DEMAND PREVIEW SERIALIZERS ====================


class DetailedBreakdownSerializer(serializers.Serializer):
    """
    Serializer for each item in the detailed_breakdown array.
    Business Logic: Represents demand vs supply for each practicum group.
    """

    practicum_type = serializers.CharField()
    program_type = serializers.CharField()
    subject_code = serializers.CharField()
    subject_display_name = serializers.CharField()
    required_slots = serializers.IntegerField()
    available_pls = serializers.IntegerField()


class SummaryCardsSerializer(serializers.Serializer):
    """
    Serializer for the summary_cards object.
    Business Logic: Aggregated metrics for allocation overview.
    """

    total_demand_slots = serializers.IntegerField()
    total_pl_capacity_slots = serializers.IntegerField()
    total_pdp_demand = serializers.IntegerField()
    total_wednesday_demand = serializers.IntegerField()


class DemandPreviewSerializer(serializers.Serializer):
    """
    Main serializer for the Demand Preview API response.
    Business Logic: Complete demand preview with summary and breakdown.
    """

    summary_cards = SummaryCardsSerializer()
    detailed_breakdown = DetailedBreakdownSerializer(many=True)


# ==================== SOLVER SERIALIZERS ====================


class AssignmentResultSerializer(serializers.Serializer):
    """
    Serializer for individual assignment result from solver.
    """

    mentor_name = serializers.CharField()
    practicum_type = serializers.CharField()
    subject = serializers.CharField()


class UnassignedMentorSerializer(serializers.Serializer):
    """
    Serializer for unassigned mentor information.
    """

    id = serializers.IntegerField()
    name = serializers.CharField()
    email = serializers.EmailField()
    reason = serializers.CharField()
    school = serializers.CharField()


class SolverResultSerializer(serializers.Serializer):
    """
    Main serializer for solver API response.
    """

    status = serializers.CharField()
    assignments = AssignmentResultSerializer(many=True)
    unassigned = UnassignedMentorSerializer(many=True)
    total_assignments = serializers.IntegerField()
    total_unassigned = serializers.IntegerField()


class AssignmentDetailSerializer(serializers.Serializer):
    """
    Serializer for detailed assignment information for results table.
    Handles both assigned slots and unallocated slots.
    """

    id = serializers.IntegerField(allow_null=True)
    student_id = serializers.CharField(allow_null=True)
    student_name = serializers.CharField(allow_null=True)
    practicum_type = serializers.CharField(allow_null=True)
    subject = serializers.CharField(allow_null=True)
    mentor_name = serializers.CharField()
    mentor_id = serializers.IntegerField()
    school_name = serializers.CharField(allow_null=True)
    status = serializers.CharField()


class AssignmentUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating assignment fields.
    Business Logic: Allows editing mentor, school, subject, practicum type.
    """

    mentor_id = serializers.IntegerField(required=False)
    school_id = serializers.IntegerField(required=False)
    subject_id = serializers.IntegerField(required=False, allow_null=True)
    practicum_type_id = serializers.IntegerField(required=False)


# ==================== STUDENT ASSIGNMENT SERIALIZERS ====================


class StudentAssignmentSerializer(serializers.ModelSerializer):
    """
    Serializer for StudentAssignment model.
    Used for listing and viewing student assignments.
    """
    student_name = serializers.SerializerMethodField()
    student_id = serializers.CharField(source="student.student_id", read_only=True)
    mentor_name = serializers.SerializerMethodField()
    school_name = serializers.CharField(source="school.name", read_only=True)
    practicum_type_code = serializers.CharField(source="practicum_type.code", read_only=True)
    practicum_type_name = serializers.CharField(source="practicum_type.name", read_only=True)
    subject_code = serializers.CharField(source="subject.code", read_only=True, allow_null=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True, allow_null=True)
    
    class Meta:
        model = StudentAssignment
        fields = [
            "id",
            "student",
            "student_id",
            "student_name",
            "mentor",
            "mentor_name",
            "school",
            "school_name",
            "practicum_type",
            "practicum_type_code",
            "practicum_type_name",
            "subject",
            "subject_code",
            "subject_name",
            "assignment_status",
            "assignment_date",
            "academic_year",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["assignment_date", "created_at", "updated_at"]
    
    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"
    
    def get_mentor_name(self, obj):
        return f"{obj.mentor.first_name} {obj.mentor.last_name}"


class StudentAssignmentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating student assignments.
    Includes validation for capacity and constraints.
    """
    
    class Meta:
        model = StudentAssignment
        fields = [
            "student",
            "mentor",
            "school",
            "practicum_type",
            "subject",
            "assignment_status",
            "academic_year",
            "notes",
        ]
    
    def validate(self, data):
        """Validate assignment constraints"""
        # Check for duplicate assignment
        existing = StudentAssignment.objects.filter(
            student=data["student"],
            practicum_type=data["practicum_type"],
            academic_year=data.get("academic_year", "2025/26")
        ).exclude(assignment_status="CANCELLED").first()
        
        if existing:
            raise serializers.ValidationError(
                f"Student is already assigned to {existing.mentor.last_name} for {data['practicum_type'].code}"
            )
        
        return data
