# in dashboard/serializers.py

from rest_framework import serializers


class AssignmentStatusSerializer(serializers.Serializer):
    """
    Serializer for assignment status per practicum type.
    """
    practicum_type = serializers.CharField()
    demand_slots = serializers.IntegerField()
    assigned_slots = serializers.IntegerField()
    unassigned_slots = serializers.IntegerField()


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
    Serializer for entity counts (students, PLs, schools).
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
    total_students_gs = serializers.IntegerField()
    total_students_ms = serializers.IntegerField()
    active_schools_total = serializers.IntegerField()
    active_schools_gs = serializers.IntegerField()
    active_schools_ms = serializers.IntegerField()
    active_schools_gms = serializers.IntegerField()


class DashboardSummarySerializer(serializers.Serializer):
    """
    Main serializer for the complete dashboard summary response.
    Validates and structures the final JSON output for the dashboard API.
    """
    assignment_status = AssignmentStatusSerializer(many=True)
    student_summary = StudentSummarySerializer()
    budget_summary = BudgetSummarySerializer()
    entity_counts = EntityCountsSerializer()



