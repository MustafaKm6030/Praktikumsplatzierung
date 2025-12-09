from django.urls import path
from .views import (
    DemandAPIView, 
    DemandPreviewAPIView,
    SolverRunAPIView,
    AssignmentListAPIView,
    ExportAssignmentsExcelAPIView,
    ExportAssignmentsPDFAPIView
)

urlpatterns = [
    path("demand/", DemandAPIView.as_view(), name="demand-api"),
    path("demand-preview/", DemandPreviewAPIView.as_view(), name="demand-preview-api"),
    path("run-solver/", SolverRunAPIView.as_view(), name="solver-run-api"),
    path("", AssignmentListAPIView.as_view(), name="assignment-list-api"),
    path("export/excel/", ExportAssignmentsExcelAPIView.as_view(), name="export-excel"),
    path("export/pdf/", ExportAssignmentsPDFAPIView.as_view(), name="export-pdf"),
]
