from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import School
from .serializers import SchoolListSerializer, SchoolDetailSerializer
from .services import get_schools_by_zone, get_schools_by_type


class SchoolViewSet(viewsets.ModelViewSet):
    """
    API endpoints for School management.
    """
    queryset = School.objects.all()
    
    def get_serializer_class(self):
        """Use different serializers for list vs detail."""
        if self.action == 'retrieve':
            return SchoolDetailSerializer
        return SchoolListSerializer
    
    @action(detail=False, methods=['get'])
    def by_zone(self, request):
        """
        Custom endpoint: GET /api/schools/by_zone/?zone=ZONE_1
        """
        zone = request.query_params.get('zone')
        schools = get_schools_by_zone(zone)
        serializer = self.get_serializer(schools, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """
        Custom endpoint: GET /api/schools/by_type/?type=GS
        """
        school_type = request.query_params.get('type')
        schools = get_schools_by_type(school_type)
        serializer = self.get_serializer(schools, many=True)
        return Response(serializer.data)
