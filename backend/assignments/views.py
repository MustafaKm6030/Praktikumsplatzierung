from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
from django.http import HttpResponse
from rest_framework.decorators import action
from .models import Assignment
from .serializers import AssignmentSerializer
from .services import adjust_mentor_assignments

from .services import (
    aggregate_demand,
    get_demand_preview_data,
    generate_assignments_excel,
    generate_assignments_pdf,
    update_assignment,
    get_mentor_capacity,
    reset_all_assignments,
)
from praktikums_lehrkraft.models import PraktikumsLehrkraft
from .serializers import (
    DemandSerializer,
    DemandPreviewSerializer,
    SolverResultSerializer,
    AssignmentDetailSerializer,
    AssignmentUpdateSerializer,
)
from .solver import run_solver


class DemandAPIView(APIView):
    """
    API endpoint to expose the aggregated practicum demand.
    """

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to calculate and return the demand.
        """
        demand_data = aggregate_demand()
        serializer = DemandSerializer(demand_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DemandPreviewAPIView(APIView):
    """
    API endpoint for demand preview on allocation page.
    Business Logic: Provides summary cards and detailed breakdown
    of student demand vs PL supply for allocation planning.
    """

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests for demand preview data.
        Returns summary_cards and detailed_breakdown.
        """
        preview_data = get_demand_preview_data()
        serializer = DemandPreviewSerializer(preview_data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SolverRunAPIView(APIView):
    """
    API endpoint to run the allocation solver.
    Business Logic: Executes the optimization algorithm and returns results.
    """

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to run the solver.
        Returns solver results with assignments and unassigned mentors.
        """
        try:
            result = run_solver()

            response_data = {
                "status": result["status"],
                "assignments": result["assignments"],
                "unassigned": result["unassigned"],
                "total_assignments": len(result["assignments"]),
                "total_unassigned": len(result["unassigned"]),
            }

            serializer = SolverResultSerializer(response_data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e), "status": "FAILURE"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AssignmentListAPIView(APIView):
    """
    API endpoint to retrieve all assignments for the results table.
    Business Logic: Returns detailed assignment information including
    student assignments (when available) and mentor details.
    Also includes unallocated slots as separate rows.
    """

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to retrieve all assignments.
        Returns list of assignment details for the results table.
        Includes both assigned slots and unallocated slots.
        """
        assignments = Assignment.objects.select_related(
            "mentor", "practicum_type", "subject", "school"
        ).all()

        assignment_list = []
        for assignment in assignments:
            assignment_list.append(
                {
                    "id": assignment.id,
                    "student_id": None,
                    "student_name": None,
                    "practicum_type": assignment.practicum_type.get_code_display(),
                    "subject": assignment.subject.code if assignment.subject else "N/A",
                    "mentor_name": f"{assignment.mentor.last_name}, {assignment.mentor.first_name}",
                    "mentor_id": assignment.mentor.id,
                    "school_name": assignment.school.name,
                    "status": "ok",
                }
            )

        unallocated_slots = self._get_unallocated_slots()
        assignment_list.extend(unallocated_slots)

        serializer = AssignmentDetailSerializer(assignment_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def _get_unallocated_slots(self):
        """
        Calculates unallocated slots for all active mentors.
        Returns a list of unallocated slot entries, one per unallocated slot.
        Only returns unallocated slots if there are actual assignments (solver has run).
        """
        unallocated_list = []
        
        total_assignments = Assignment.objects.count()
        if total_assignments == 0:
            return unallocated_list
        
        active_mentors = PraktikumsLehrkraft.objects.filter(is_active=True).select_related("school")
        
        assignment_counts = {}
        for assignment in Assignment.objects.select_related("mentor").all():
            mentor_id = assignment.mentor.id
            assignment_counts[mentor_id] = assignment_counts.get(mentor_id, 0) + 1
        
        for mentor in active_mentors:
            capacity = get_mentor_capacity(mentor)
            assigned_count = assignment_counts.get(mentor.id, 0)
            unallocated_count = capacity - assigned_count
            
            for _ in range(unallocated_count):
                unallocated_list.append(
                    {
                        "id": None,
                        "student_id": None,
                        "student_name": None,
                        "practicum_type": None,
                        "subject": None,
                        "mentor_name": f"{mentor.last_name}, {mentor.first_name}",
                        "mentor_id": mentor.id,
                        "school_name": mentor.school.name if mentor.school else None,
                        "status": "unallocated",
                    }
                )
        
        return unallocated_list


class ExportAssignmentsExcelAPIView(APIView):
    """
    API endpoint to export assignments as Excel.
    Business Logic: Generate Excel file with all assignment details.
    """

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to export assignments as Excel.
        Returns Excel file download response.
        """
        try:
            excel_content = generate_assignments_excel()

            response = HttpResponse(
                excel_content,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = (
                'attachment; filename="praktikumszuteilungen.xlsx"'
            )

            return response

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExportAssignmentsPDFAPIView(APIView):
    """
    API endpoint to export assignments as PDF.
    Business Logic: Generate PDF report with all assignment details.
    """

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to export assignments as PDF.
        Returns PDF file download response.
        """
        try:
            pdf_content = generate_assignments_pdf()

            response = HttpResponse(pdf_content, content_type="application/pdf")
            response["Content-Disposition"] = (
                'attachment; filename="praktikumszuteilungen.pdf"'
            )

            return response

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AssignmentUpdateAPIView(APIView):
    """
    API endpoint to update an assignment.
    Business Logic: Allows manual adjustment of assignment fields.
    """

    def patch(self, request, assignment_id, *args, **kwargs):
        """
        Handles PATCH requests to update assignment.
        Allows updating mentor, school, subject, practicum type.
        """
        serializer = AssignmentUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        result, status_code = update_assignment(
            assignment_id, serializer.validated_data
        )

        if status_code == 200:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status_code)


class ResetAssignmentsAPIView(APIView):
    """
    API endpoint to reset (delete) all assignments.
    Business Logic: Provides ability to clear all allocation results
    and start fresh allocation cycle.
    """

    def delete(self, request, *args, **kwargs):
        """
        Handles DELETE requests to remove all assignments.
        Returns success message with count of deleted records.
        """
        try:
            result = reset_all_assignments()
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e), "success": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AssignmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing the final Assignment results.
    """

    queryset = Assignment.objects.all().select_related(
        "mentor", "practicum_type", "subject", "school"
    )
    serializer_class = AssignmentSerializer

    @action(detail=False, methods=["post"])
    def adjust(self, request):
        """
        POST /api/assignments/adjust/
        Manually overrides the assignments for a single mentor.
        """
        mentor_id = request.data.get("mentor_id")
        proposed = request.data.get("proposed_assignments", [])
        force = request.data.get("force_override", False)

        if not mentor_id:
            return Response(
                {"error": "mentor_id is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            new_assignments = adjust_mentor_assignments(mentor_id, proposed, force)
            serializer = self.get_serializer(new_assignments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError as e:
            # Catch validation errors from the service
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            # Catch unexpected server errors
            return Response(
                {"error": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
