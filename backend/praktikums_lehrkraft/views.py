from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from .models import PraktikumsLehrkraft
from .serializers import PLListSerializer, PLDetailSerializer, PLCreateUpdateSerializer
from .services import (
    get_pls_by_school,
    get_pls_by_program,
    search_pls,
    get_available_pls_for_praktikum,
    get_pl_capacity_info,
    get_pls_by_subject,
    import_pls_from_csv,
    export_pls_to_csv,
)


class PLViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Praktikumslehrkräfte (PLs).
    Refactored for new data model.
    """

    # Updated queryset to remove deleted relations
    queryset = (
        PraktikumsLehrkraft.objects.all()
        .select_related("school", "main_subject")
        .prefetch_related("available_praktikum_types", "available_subjects")
    )
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["school", "program", "is_active", "school__school_type"]
    search_fields = ["first_name", "last_name", "email", "school__name"]
    ordering_fields = ["last_name", "first_name", "email", "school__name"]
    ordering = ["last_name", "first_name"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PLDetailSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return PLCreateUpdateSerializer
        return PLListSerializer

    def create(self, request, *args, **kwargs):
        """
        POST /api/pls/ - Create new PL.
        Business Logic: Creates new Praktikumslehrkraft with validation.
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
        PUT /api/pls/{id}/ - Full update of PL.
        Business Logic: Updates all fields of existing PL.
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH /api/pls/{id}/ - Partial update of PL.
        Business Logic: Updates only specified fields.
        """
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        DELETE /api/pls/{id}/ - Delete PL from database.
        Business Logic: Permanently removes PL and related records.
        """
        instance = self.get_object()
        instance.delete()
        return Response(
            {"message": "PL deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=False, methods=["get"])
    def by_school(self, request):
        """
        Returns PLs filtered by school.
        """
        school_id = request.query_params.get("school_id")
        if not school_id:
            return Response(
                {"error": "school_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pls = get_pls_by_school(school_id)
        serializer = PLListSerializer(pls, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_program(self, request):
        """
        Returns PLs filtered by program (GS or MS).
        """
        program = request.query_params.get("program")
        if not program:
            return Response(
                {"error": "program parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pls = get_pls_by_program(program)
        serializer = PLListSerializer(pls, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def search(self, request):
        """
        Search PLs by name, school, or ID.
        """
        search_term = request.query_params.get("q", "")
        if not search_term:
            return Response(
                {"error": "q parameter is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        pls = search_pls(search_term)
        serializer = PLListSerializer(pls, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def available_for_praktikum(self, request):
        """
        Returns PLs available for specific praktikum type and subject.
        """
        praktikum_type_id = request.query_params.get("praktikum_type_id")
        subject_id = request.query_params.get("subject_id")

        if not praktikum_type_id:
            return Response(
                {"error": "praktikum_type_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pls = get_available_pls_for_praktikum(praktikum_type_id, subject_id)
        serializer = PLListSerializer(pls, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def capacity_info(self, request, pk=None):
        """
        Returns capacity information for a specific PL.
        """
        try:
            capacity_info = get_pl_capacity_info(pk)
            return Response(capacity_info)
        except PraktikumsLehrkraft.DoesNotExist:
            return Response({"error": "PL not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["get"])
    def by_subject(self, request):
        """
        Returns PLs who can teach a specific subject.
        """
        subject_id = request.query_params.get("subject_id")

        if not subject_id:
            return Response(
                {"error": "subject_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pls = get_pls_by_subject(subject_id)
        serializer = PLListSerializer(pls, many=True)
        return Response(serializer.data)

    @action(
        detail=False, methods=["post"], parser_classes=[MultiPartParser, FormParser]
    )
    def import_csv(self, request):
        """
        POST /api/pls/import_csv/ - Import PLs from CSV or Excel.
        Business Logic: Bulk creates/updates PLs from uploaded CSV or Excel file.
        """
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response(
                {"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        allowed_extensions = ".xlsx", ".xls"
        if not file_obj.name.endswith(allowed_extensions):
            return Response(
                {"error": "File must be an Excel file (.xlsx or .xls)"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = import_pls_from_csv(file_obj)
            return Response(result, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def export(self, request):
        """
        GET /api/pls/export/ - Export PLs to CSV.
        Business Logic: Generates CSV file with all PLs data.
        """
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="pls_export.csv"'

        csv_data = export_pls_to_csv()
        response.write(csv_data)

        return response
