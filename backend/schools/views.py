from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import School
from .serializers import SchoolListSerializer, SchoolDetailSerializer

# Import the refactored services
from .services import (
    get_schools_by_zone,
    get_schools_by_type,
    get_school_capacity,
    get_schools_for_wednesday_praktika,
)


class SchoolViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Schools.
    Refactored to align with the CSV data source.
    """

    queryset = School.objects.all().order_by("name")
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["school_type", "district", "zone", "opnv_code", "is_active"]
    search_fields = ["name", "city", "district"]
    ordering_fields = ["name", "school_type", "distance_km"]
    ordering = ["name"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SchoolDetailSerializer
        return SchoolListSerializer

    @action(detail=False, methods=["get"])
    def by_zone(self, request):
        """Returns schools filtered by a specific zone."""
        zone = request.query_params.get("zone")
        if not zone:
            return Response(
                {"error": "zone parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        schools = get_schools_by_zone(zone)
        serializer = self.get_serializer(schools, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_type(self, request):
        """Returns schools filtered by a specific school type (GS or MS)."""
        school_type = request.query_params.get("type")
        if not school_type:
            return Response(
                {"error": "type parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        schools = get_schools_by_type(school_type)
        serializer = self.get_serializer(schools, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def capacity(self, request, pk=None):
        """
        Calculates and returns the dynamic capacity for a single school.
        """
        try:
            school_capacity_data = get_school_capacity(pk)
            return Response(school_capacity_data)
        except School.DoesNotExist:
            return Response(
                {"error": "School not found"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=["get"])
    def for_wednesday_praktika(self, request):
        """
        Returns a list of all schools that are valid for SFP and ZSP assignments.
        """
        schools = get_schools_for_wednesday_praktika()
        serializer = self.get_serializer(schools, many=True)
        return Response(serializer.data)
