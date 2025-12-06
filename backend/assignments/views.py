from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .services import aggregate_demand, get_demand_preview_data
from .serializers import DemandSerializer, DemandPreviewSerializer


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
