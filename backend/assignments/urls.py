from django.urls import path
from .views import DemandAPIView

urlpatterns = [
    path("demand/", DemandAPIView.as_view(), name="demand-api"),
]
