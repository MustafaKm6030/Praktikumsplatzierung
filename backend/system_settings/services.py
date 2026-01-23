from .models import SystemSettings


def get_active_settings():
    """
    Get the currently active system settings.
    Business Logic: Returns the active academic year settings or creates default if none exist.
    """
    settings = SystemSettings.objects.filter(is_active=True).first()
    
    if not settings:
        # Create default settings if none exist
        settings = SystemSettings.objects.create(
            current_academic_year='2024/2025',
            total_anrechnungsstunden_budget=210.0,
            gs_budget_percentage=80.48,
            ms_budget_percentage=19.52,
            university_name='Universität Passau',
            is_active=True,
            core_subjects=["D", "MA"]
        )
    
    return settings


def update_settings(settings_id, data):
    """
    Update system settings.
    Business Logic: Updates settings and ensures only one active setting exists.
    """
    try:
        settings = SystemSettings.objects.get(id=settings_id)
        
        # If activating this settings, deactivate all others
        if data.get('is_active', False):
            SystemSettings.objects.exclude(id=settings_id).update(is_active=False)
        
        # Update fields
        for key, value in data.items():
            setattr(settings, key, value)
        
        settings.save()
        return settings
    except SystemSettings.DoesNotExist:
        return None


def calculate_budget_allocation(settings):
    """
    Calculate budget allocation details.
    Business Logic: Computes GS and MS budget hours based on percentages.
    """
    gs_hours = settings.total_anrechnungsstunden_budget * settings.gs_budget_percentage / 100
    ms_hours = settings.total_anrechnungsstunden_budget * settings.ms_budget_percentage / 100
    
    return {
        'total_budget': float(settings.total_anrechnungsstunden_budget),
        'gs_percentage': float(settings.gs_budget_percentage),
        'ms_percentage': float(settings.ms_budget_percentage),
        'gs_hours': float(gs_hours),
        'ms_hours': float(ms_hours),
    }


def get_all_settings():
    """
    Get all system settings (historical + current).
    Business Logic: Returns all settings ordered by academic year.
    """
    return SystemSettings.objects.all().order_by('-current_academic_year')


def set_active_academic_year(academic_year):
    """
    Set a specific academic year as active.
    Business Logic: Deactivates all other years and activates the specified one.
    """
    # Deactivate all settings
    SystemSettings.objects.all().update(is_active=False)
    
    # Activate the specified year
    settings = SystemSettings.objects.filter(current_academic_year=academic_year).first()
    if settings:
        settings.is_active = True
        settings.save()
        return settings
    
    return None

