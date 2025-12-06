from django.urls import path
from .views import DemandAPIView, DemandPreviewAPIView

urlpatterns = [
    path("demand/", DemandAPIView.as_view(), name="demand-api"),
    path("demand-preview/", DemandPreviewAPIView.as_view(), name="demand-preview-api"),
]
