from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Subject, PraktikumType
from .serializers import SubjectSerializer, PraktikumTypeSerializer
from .services import get_filtered_subjects_for_assignment, get_all_subjects_from_rules


class SubjectViewSet(viewsets.ModelViewSet):
    """
    API endpoints for Subject management.
    
    list: Get all subjects
    retrieve: Get a specific subject
    create: Create a new subject
    update: Update a subject
    destroy: Delete a subject
    """
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    # permission_classes = [IsAuthenticated]  # Uncomment when auth is ready

    @action(detail=False, methods=['get'])
    def filtered(self, request):
        """
        Get subjects filtered by praktikum type and school type.
        
        Query params:
        - praktikum_type: ZSP, SFP, PDP1, PDP2
        - school_type: GS, MS, GMS
        """
        praktikum_type = request.query_params.get('praktikum_type')
        school_type = request.query_params.get('school_type')
        
        if not praktikum_type:
            return Response(
                {'error': 'praktikum_type is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not school_type:
            return Response(
                {'error': 'school_type is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        subjects = get_filtered_subjects_for_assignment(
            praktikum_type=praktikum_type,
            school_type=school_type
        )
        
        return Response(subjects)
    
    @action(detail=False, methods=['get'])
    def from_rules(self, request):
        """
        Get all unique subjects from subject_grouping_rules.json.
        Returns subjects with code and display_name.
        """
        subjects = get_all_subjects_from_rules()
        return Response(subjects)


class PraktikumTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoints for Praktikum Type management.
    
    list: Get all praktikum types
    retrieve: Get a specific praktikum type
    create: Create a new praktikum type
    update: Update a praktikum type
    destroy: Delete a praktikum type
    """
    queryset = PraktikumType.objects.all()
    serializer_class = PraktikumTypeSerializer
    # permission_classes = [IsAuthenticated]
