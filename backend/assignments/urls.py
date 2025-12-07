from django.urls import path
from .views import (
    DemandAPIView, 
    DemandPreviewAPIView,
    SolverRunAPIView,
    AssignmentListAPIView
)

urlpatterns = [
    path("demand/", DemandAPIView.as_view(), name="demand-api"),
    path("demand-preview/", DemandPreviewAPIView.as_view(), name="demand-preview-api"),
    path("run-solver/", SolverRunAPIView.as_view(), name="solver-run-api"),
    path("", AssignmentListAPIView.as_view(), name="assignment-list-api"),
]
