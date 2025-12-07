from rest_framework import serializers


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
    """
    id = serializers.IntegerField()
    student_id = serializers.CharField(allow_null=True)
    student_name = serializers.CharField(allow_null=True)
    practicum_type = serializers.CharField()
    subject = serializers.CharField(allow_null=True)
    mentor_name = serializers.CharField()
    school_name = serializers.CharField()
    status = serializers.CharField()