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
    # ==================== STUDENT ASSIGNMENT ENDPOINTS ====================

    @action(detail=True, methods=["get"])
    def assignment(self, request, pk=None):
        """Get a student's current praktikum assignment"""
        student = self.get_object()
        from assignments.models import StudentAssignment
        from assignments.serializers import StudentAssignmentSerializer

        assignment = StudentAssignment.objects.filter(
            student=student
        ).exclude(assignment_status="CANCELLED").first()

        if not assignment:
            return Response(
                {"message": "Student has no active assignment"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = StudentAssignmentSerializer(assignment)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        """Assign a student to a mentor/school for a practicum"""
        student = self.get_object()
        from assignments.models import StudentAssignment
        from assignments.serializers import StudentAssignmentCreateSerializer

        # Add student to the request data
        data = request.data.copy()
        data["student"] = student.id

        serializer = StudentAssignmentCreateSerializer(data=data)
        if serializer.is_valid():
            assignment = serializer.save()
            
            # Update student placement status
            student.placement_status = "PLACED"
            student.save()
            
            from assignments.serializers import StudentAssignmentSerializer
            response_serializer = StudentAssignmentSerializer(assignment)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["patch"])
    def reassign(self, request, pk=None):
        """Reassign a student to a different mentor"""
        student = self.get_object()
        from assignments.models import StudentAssignment

        practicum_type_id = request.data.get("practicum_type")
        if not practicum_type_id:
            return Response(
                {"error": "practicum_type is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        assignment = StudentAssignment.objects.filter(
            student=student,
            practicum_type_id=practicum_type_id
        ).exclude(assignment_status="CANCELLED").first()

        if not assignment:
            return Response(
                {"error": "No active assignment found for this practicum type"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Update assignment fields
        if "mentor" in request.data:
            assignment.mentor_id = request.data["mentor"]
        if "school" in request.data:
            assignment.school_id = request.data["school"]
        if "subject" in request.data:
            assignment.subject_id = request.data["subject"]
        if "assignment_status" in request.data:
            assignment.assignment_status = request.data["assignment_status"]
        if "notes" in request.data:
            assignment.notes = request.data["notes"]

        assignment.save()
        
        from assignments.serializers import StudentAssignmentSerializer
        serializer = StudentAssignmentSerializer(assignment)
        return Response(serializer.data)

    @action(detail=True, methods=["delete"], url_path="assignment/(?P<practicum_type_id>[^/.]+)")
    def remove_assignment(self, request, pk=None, practicum_type_id=None):
        """Remove a student's assignment"""
        student = self.get_object()
        from assignments.models import StudentAssignment

        assignment = StudentAssignment.objects.filter(
            student=student,
            practicum_type_id=practicum_type_id
        ).exclude(assignment_status="CANCELLED").first()

        if not assignment:
            return Response(
                {"error": "No active assignment found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        assignment.assignment_status = "CANCELLED"
        assignment.save()
        
        # Check if student has any other active assignments
        has_other_assignments = StudentAssignment.objects.filter(
            student=student
        ).exclude(assignment_status="CANCELLED").exists()
        
        if not has_other_assignments:
            student.placement_status = "UNPLACED"
            student.save()

        return Response(
            {"message": "Assignment removed successfully"},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def unassigned(self, request):
        """Get list of all unassigned students"""
        unassigned_students = Student.objects.filter(
            placement_status="UNPLACED"
        ).order_by("last_name", "first_name")

        serializer = self.get_serializer(unassigned_students, many=True)
        return Response(serializer.data)
    @action(detail=False, methods=["get"])
    def export(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="students_export.csv"'

        csv_data = export_students_to_csv()
        response.write(csv_data)

        return response

    @action(
        detail=False, methods=["post"], parser_classes=[MultiPartParser, FormParser]
    )
    def import_excel(self, request):
        """Import students from Excel file (.xlsx)"""
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response(
                {"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not file_obj.name.endswith(".xlsx"):
            return Response(
                {"error": "File must be an Excel file (.xlsx)"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from .services import import_students_from_excel
            result = import_students_from_excel(file_obj)
            return Response(result, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def export_excel(self, request):
        """Export students to Excel file (.xlsx)"""
        try:
            from .services import export_students_to_excel
            
            response = HttpResponse(
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response["Content-Disposition"] = 'attachment; filename="students_export.xlsx"'

            excel_data = export_students_to_excel()
            response.write(excel_data)

            return response
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
