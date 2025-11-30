# in dashboard/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .services import get_dashboard_summary_data
from .serializers import DashboardSummarySerializer


class DashboardSummaryView(APIView):
    """
    API endpoint for consolidated dashboard data.
    Returns aggregated data for assignment status, budget, and entity counts.
    """
    
    def get(self, request):
        """
        GET /api/dashboard/summary
        Returns the complete dashboard summary data.
        """
        # Get aggregated data from service layer
        data = get_dashboard_summary_data()
        
        # Validate and serialize the response
        serializer = DashboardSummarySerializer(data)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
