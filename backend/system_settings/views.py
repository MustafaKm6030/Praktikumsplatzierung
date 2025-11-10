from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import SystemSettings
from .serializers import SystemSettingsSerializer
from .services import (
    get_active_settings,
    update_settings,
    calculate_budget_allocation,
    get_all_settings,
    set_active_academic_year
)


class SystemSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing System Settings.
    Business Logic: Provides endpoints for system-wide configuration management.
    
    Endpoints:
    - GET /api/settings/ - Get active settings (or all settings)
    - GET /api/settings/{id}/ - Get specific settings by ID
    - POST /api/settings/ - Create new settings
    - PUT /api/settings/{id}/ - Update settings
    - PATCH /api/settings/{id}/ - Partial update settings
    - DELETE /api/settings/{id}/ - Delete settings
    """
    queryset = SystemSettings.objects.all()
    serializer_class = SystemSettingsSerializer
    
    def list(self, request, *args, **kwargs):
        """
        GET /api/settings/ - Get active settings.
        Business Logic: Returns currently active system settings.
        """
        settings = get_active_settings()
        serializer = self.get_serializer(settings)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """
        POST /api/settings/ - Create new settings.
        Business Logic: Creates new academic year settings.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # If this is set to active, deactivate all others
        if serializer.validated_data.get('is_active', False):
            SystemSettings.objects.all().update(is_active=False)
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        """
        PUT /api/settings/{id}/ - Full update of settings.
        Business Logic: Updates all fields of settings.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # If activating this settings, deactivate all others
        if serializer.validated_data.get('is_active', False):
            SystemSettings.objects.exclude(id=instance.id).update(is_active=False)
        
        self.perform_update(serializer)
        return Response(serializer.data)
    
    def partial_update(self, request, *args, **kwargs):
        """
        PATCH /api/settings/{id}/ - Partial update of settings.
        Business Logic: Updates only specified fields.
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        DELETE /api/settings/{id}/ - Delete settings.
        Business Logic: Removes settings from database.
        """
        instance = self.get_object()
        
        # Prevent deletion of active settings
        if instance.is_active:
            return Response(
                {'error': 'Cannot delete active settings. Please activate another setting first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        instance.delete()
        return Response(
            {'message': 'Settings deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=True, methods=['get'])
    def budget_allocation(self, request, pk=None):
        """
        GET /api/settings/{id}/budget_allocation/ - Get budget allocation details.
        Business Logic: Returns calculated budget distribution.
        """
        settings = self.get_object()
        allocation = calculate_budget_allocation(settings)
        return Response(allocation)
    
    @action(detail=False, methods=['get'])
    def all(self, request):
        """
        GET /api/settings/all/ - Get all settings (historical + current).
        Business Logic: Returns all academic year settings.
        """
        settings = get_all_settings()
        serializer = self.get_serializer(settings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def activate(self, request):
        """
        POST /api/settings/activate/ - Activate specific academic year.
        Business Logic: Sets specified academic year as active.
        Request Body: {'academic_year': '2024/2025'}
        """
        academic_year = request.data.get('academic_year')
        
        if not academic_year:
            return Response(
                {'error': 'academic_year is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        settings = set_active_academic_year(academic_year)
        
        if not settings:
            return Response(
                {'error': f'Settings for academic year {academic_year} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(settings)
        return Response(serializer.data)
