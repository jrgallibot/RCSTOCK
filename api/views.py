from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated

from app.backend.models import TblFaq, TblContactUs
from api.serializers import FaqSerializer, QueriesSerializer


class FaqView(generics.ListAPIView):
	queryset = TblFaq.objects.all().order_by('-id')
	serializer_class = FaqSerializer
	permission_classes = [IsAuthenticated]

class QueriesView(generics.ListAPIView):
	queryset = TblContactUs.objects.all().order_by('-date_added')
	serializer_class = QueriesSerializer
	permission_classes = [IsAuthenticated]