from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from .models import Student
from .serializers import (
    StudentListSerializer,
    StudentDetailSerializer,
    StudentCreateUpdateSerializer,
)
from .services import (
    get_students_by_program,
    get_students_by_region,
    import_students_from_csv,
    export_students_to_csv,
)


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["program", "home_region", "placement_status"]
    search_fields = ["student_id", "first_name", "last_name", "email", "major"]
    ordering_fields = ["last_name", "first_name", "student_id"]
    ordering = ["last_name", "first_name"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return StudentDetailSerializer
        if self.action in ["create", "update", "partial_update"]:
            return StudentCreateUpdateSerializer
        return StudentListSerializer

    @action(detail=False, methods=["get"])
    def by_program(self, request):
        program = request.query_params.get("program")
        if not program:
            return Response({"error": "program required"}, status=400)
        students = get_students_by_program(program)
        serializer = self.get_serializer(students, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_region(self, request):
        region = request.query_params.get("region")
        if not region:
            return Response({"error": "region required"}, status=400)
        students = get_students_by_region(region)
        serializer = self.get_serializer(students, many=True)
        return Response(serializer.data)

    @action(
        detail=False, methods=["post"], parser_classes=[MultiPartParser, FormParser]
    )
    def import_csv(self, request):
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
            result = import_students_from_csv(file_obj)
            return Response(result, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def export(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="students_export.csv"'

        csv_data = export_students_to_csv()
        response.write(csv_data)

        return response
