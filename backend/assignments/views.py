from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse

from .services import (
    aggregate_demand,
    get_demand_preview_data,
    generate_assignments_excel,
    generate_assignments_pdf
)
from .serializers import (
    DemandSerializer,
    DemandPreviewSerializer,
    SolverResultSerializer,
    AssignmentDetailSerializer,
)
from .solver import run_solver
from .models import Assignment


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
    """

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to retrieve all assignments.
        Returns list of assignment details for the results table.
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
                    "school_name": assignment.school.name,
                    "status": "ok",
                }
            )

        serializer = AssignmentDetailSerializer(assignment_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="praktikumszuteilungen.xlsx"'
            
            return response
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
            
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="praktikumszuteilungen.pdf"'
            
            return response
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
