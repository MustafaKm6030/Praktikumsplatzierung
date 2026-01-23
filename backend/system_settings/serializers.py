from rest_framework import serializers
from .models import SystemSettings


class SystemSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for System Settings.
    Business Logic: Handles system-wide configuration including academic year,
    budget allocation, and key deadlines.
    """
    # Computed fields
    gs_budget_hours = serializers.SerializerMethodField()
    ms_budget_hours = serializers.SerializerMethodField()
    
    class Meta:
        model = SystemSettings
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_gs_budget_hours(self, obj):
        """Calculate GS budget in hours."""
        return float(obj.total_anrechnungsstunden_budget * obj.gs_budget_percentage / 100)
    
    def get_ms_budget_hours(self, obj):
        """Calculate MS budget in hours."""
        return float(obj.total_anrechnungsstunden_budget * obj.ms_budget_percentage / 100)
    
    def validate(self, data):
        """
        Validate budget percentages sum to 100%.
        Business Logic: GS and MS percentages must total 100%.
        """
        gs_pct = data.get('gs_budget_percentage', getattr(self.instance, 'gs_budget_percentage', 0))
        ms_pct = data.get('ms_budget_percentage', getattr(self.instance, 'ms_budget_percentage', 0))
        
        total = float(gs_pct) + float(ms_pct)
        if abs(total - 100.0) > 0.01:  # Allow small floating point differences
            raise serializers.ValidationError({
                'budget_percentages': f'GS and MS budget percentages must sum to 100%. Current sum: {total}%'
            })
        
        return data
    
    def validate_current_academic_year(self, value):
        """
        Validate academic year format.
        Business Logic: Should be in format 'YYYY/YYYY' (e.g., '2024/2025').
        """
        if '/' not in value:
            raise serializers.ValidationError("Academic year must be in format 'YYYY/YYYY' (e.g., '2024/2025')")
        
        parts = value.split('/')
        if len(parts) != 2:
            raise serializers.ValidationError("Academic year must be in format 'YYYY/YYYY'")
        
        try:
            year1 = int(parts[0])
            year2 = int(parts[1])
            if year2 != year1 + 1:
                raise serializers.ValidationError("Second year must be exactly one year after the first")
        except ValueError:
            raise serializers.ValidationError("Invalid year format")
        
        return value
    
    def validate_core_subjects(self, value):
        """
        Validate core subjects format.
        Business Logic: Must be a list of strings (subject codes).
        """
        if not isinstance(value, list):
            raise serializers.ValidationError("Core subjects must be a list")
        
        for item in value:
            if not isinstance(item, str):
                raise serializers.ValidationError("All core subjects must be strings (subject codes)")
            if not item.strip():
                raise serializers.ValidationError("Core subjects cannot contain empty strings")
        
        return value

