from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from app.backend.models import Loghistory
from api.settings.serializers import LogsSerializer


class LogsView(generics.ListAPIView):
	queryset = Loghistory.objects.all().order_by('-datetime_added')
	serializer_class = LogsSerializer
	permission_classes = [IsAuthenticated]


