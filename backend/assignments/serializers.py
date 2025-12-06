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
