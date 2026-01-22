# in dashboard/serializers.py

from rest_framework import serializers


class StudentSummarySerializer(serializers.Serializer):
    """
    Serializer for student summary data.
    """
    total_students = serializers.IntegerField()
    assigned_students = serializers.IntegerField()
    unassigned_students = serializers.IntegerField()


class BudgetSummarySerializer(serializers.Serializer):
    """
    Serializer for budget summary data.
    """
    total_budget = serializers.FloatField()
    distributed_gs = serializers.FloatField()
    distributed_ms = serializers.FloatField()
    remaining_budget = serializers.FloatField()


class EntityCountsSerializer(serializers.Serializer):
    """
    Serializer for entity counts (students, PLs).
    """
    total_students = serializers.IntegerField()
    unplaced_students = serializers.IntegerField()
    placed_students = serializers.IntegerField()
    unplaced_students_gs = serializers.IntegerField()
    unplaced_students_ms = serializers.IntegerField()
    placed_students_gs = serializers.IntegerField()
    placed_students_ms = serializers.IntegerField()
    active_pls_total = serializers.IntegerField()
    active_pls_gs = serializers.IntegerField()
    active_pls_ms = serializers.IntegerField()


class DashboardSummarySerializer(serializers.Serializer):
    """
    Main serializer for the complete dashboard summary response.
    Validates and structures the final JSON output for the dashboard API.
    """
    student_summary = StudentSummarySerializer()
    budget_summary = BudgetSummarySerializer()
    entity_counts = EntityCountsSerializer()



