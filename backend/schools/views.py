from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
import csv
import io
from .models import School
from .serializers import SchoolListSerializer, SchoolDetailSerializer, SchoolImportSerializer
from .services import get_schools_by_zone, get_schools_by_type, import_schools_from_csv, export_schools_to_csv


class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['school_type', 'district', 'opnv_zone', 'is_active']
    search_fields = ['name', 'address', 'city', 'district', 'contact_person']
    ordering_fields = ['name', 'school_type', 'travel_time_minutes']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SchoolDetailSerializer
        return SchoolListSerializer
    
    @action(detail=False, methods=['get'])
    def by_zone(self, request):
        zone = request.query_params.get('zone')
        schools = get_schools_by_zone(zone)
        serializer = self.get_serializer(schools, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        school_type = request.query_params.get('type')
        schools = get_schools_by_type(school_type)
        serializer = self.get_serializer(schools, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def import_csv(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not file_obj.name.endswith('.csv'):
            return Response(
                {'error': 'File must be a CSV'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            result = import_schools_from_csv(file_obj)
            return Response(result, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="schools_export.csv"'
        
        csv_data = export_schools_to_csv()
        response.write(csv_data)
        
        return response
