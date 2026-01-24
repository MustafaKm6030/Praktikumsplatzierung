from django.urls import path, include
from .views import (
    DemandAPIView,
    DemandPreviewAPIView,
    SolverRunAPIView,
    AssignmentListAPIView,
    ExportAssignmentsExcelAPIView,
    ExportAssignmentsPDFAPIView,
    AssignmentUpdateAPIView,
    AssignmentViewSet,
    ResetAssignmentsAPIView,
    AssignmentStatusAPIView,
    AssignmentOptionsAPIView,
)
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r"assignments", AssignmentViewSet, basename="assignment")

urlpatterns = [
    path("demand/", DemandAPIView.as_view(), name="demand-api"),
    path("demand-preview/", DemandPreviewAPIView.as_view(), name="demand-preview-api"),
    path("run-solver/", SolverRunAPIView.as_view(), name="solver-run-api"),
    path("", AssignmentListAPIView.as_view(), name="assignment-list-api"),
    path(
        "<int:assignment_id>/update/",
        AssignmentUpdateAPIView.as_view(),
        name="assignment-update",
    ),
    path("export/excel/", ExportAssignmentsExcelAPIView.as_view(), name="export-excel"),
    path("export/pdf/", ExportAssignmentsPDFAPIView.as_view(), name="export-pdf"),
    path("reset/", ResetAssignmentsAPIView.as_view(), name="reset-assignments"),
    path("status/", AssignmentStatusAPIView.as_view(), name="assignment-status"),
    path("options/", AssignmentOptionsAPIView.as_view(), name="assignment-options"),
    path("", include(router.urls)),
]
