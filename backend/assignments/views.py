from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .services import aggregate_demand
from .serializers import DemandSerializer


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
