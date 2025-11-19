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
