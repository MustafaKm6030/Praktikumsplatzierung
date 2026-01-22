from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from .models import School
from .serializers import (
    SchoolListSerializer,
    SchoolDetailSerializer,
    SchoolCreateUpdateSerializer,
)

# Import the refactored services
from .services import (
    get_schools_by_zone,
    get_schools_by_type,
    get_school_capacity,
    get_schools_for_wednesday_praktika,
    import_schools_from_csv,
    export_schools_to_csv,
    geocode_schools_batch,
)


class SchoolViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Schools.
    Refactored to align with the CSV data source.
    """

    queryset = School.objects.filter(is_active=True).order_by("name")
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
        if self.action in ["create", "update", "partial_update"]:
            return SchoolCreateUpdateSerializer
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

    def create(self, request, *args, **kwargs):
        """
        POST /api/schools/ - Create new school.
        Business Logic: Creates new school with validation.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        """
        PUT /api/schools/{id}/ - Full update of school.
        Business Logic: Updates all fields of existing school.
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH /api/schools/{id}/ - Partial update of school.
        Business Logic: Updates only specified fields.
        """
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        DELETE /api/schools/{id}/ - Soft delete school.
        Business Logic: Sets is_active=False instead of hard delete.
        This preserves data integrity for existing assignments.
        """
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(
            {"message": "School deleted successfully"},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False, methods=["post"], parser_classes=[MultiPartParser, FormParser]
    )
    def import_csv(self, request):
        """
        POST /api/schools/import_csv/ - Import schools from CSV.
        Business Logic: Bulk creates/updates schools from uploaded CSV file.
        """
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response(
                {"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not file_obj.name.endswith(".csv"):
            return Response(
                {"error": "File must be a CSV"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            result = import_schools_from_csv(file_obj)
            return Response(result, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def export(self, request):
        """
        GET /api/schools/export/ - Export schools to CSV.
        Business Logic: Generates CSV file with all schools data.
        """
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="schools_export.csv"'

        csv_data = export_schools_to_csv()
        response.write(csv_data)

        return response

    @action(detail=False, methods=["post"])
    def geocode_pending(self, request):
        """
        POST /api/schools/geocode_pending/ - Trigger geocoding for all pending schools.
        Business Logic: Geocodes all schools with 'pending' or 'failed' status.

        This endpoint should be called from a background job or admin action.
        It will take time proportional to the number of schools (1.1s per school).
        """
        retry_failed = request.data.get("retry_failed", False)

        statuses = ["pending"]
        if retry_failed:
            statuses.append("failed")

        schools_to_geocode = School.objects.filter(geocoding_status__in=statuses)
        count = schools_to_geocode.count()

        if count == 0:
            return Response(
                {
                    "message": "No schools need geocoding",
                    "stats": {"total": 0, "success": 0, "failed": 0, "skipped": 0},
                }
            )

        estimated_time = count * 1.1

        stats = geocode_schools_batch(schools_to_geocode, delay_between_requests=1.1)

        return Response(
            {
                "message": f"Geocoding complete. Processed {count} schools in ~{int(estimated_time)}s",
                "stats": stats,
            }
        )

    @action(detail=False, methods=["get"])
    def geocoding_stats(self, request):
        """
        GET /api/schools/geocoding_stats/ - Get statistics about geocoding status.
        Business Logic: Returns counts of schools by geocoding status.
        """
        from django.db.models import Count

        stats = School.objects.values("geocoding_status").annotate(count=Count("id"))

        result = {
            "pending": 0,
            "success": 0,
            "failed": 0,
            "not_needed": 0,
            "total": School.objects.count(),
        }

        for stat in stats:
            status_key = stat["geocoding_status"]
            if status_key in result:
                result[status_key] = stat["count"]

        return Response(result)

    @action(detail=False, methods=["post"])
    def run_geocoding_task(self, request):
        """
        Triggers the geocoding management command SYNCHRONOUSLY.
        """
        # Collapse imports to single line or move to top of file if possible
        from .services import geocode_schools_batch, GeocodingConnectionError

        try:
            schools = self._get_schools_for_geocoding(request.data.get("retry_failed"))
            stats = geocode_schools_batch(schools)

            if stats.get("connection_error"):
                return Response(
                    {
                        "message": "Geocoding stopped due to connection error.",
                        "stats": stats,
                        "error": stats["connection_error"],
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

            return Response(
                {"message": "Geocoding process complete.", "stats": stats},
                status=status.HTTP_200_OK,
            )

        except GeocodingConnectionError as e:
            return Response(
                {"error": f"Connection lost during geocoding: {str(e)}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _get_schools_for_geocoding(self, retry_failed):
        statuses = ["pending"]
        if retry_failed:
            statuses.append("failed")
        return School.objects.filter(geocoding_status__in=statuses)
