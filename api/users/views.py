from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from app.backend.models import Supplier
from app.models import AuthUser
from api.users.serializers import AuthUserSerializer, SuppliersSerializer


class UserlistView(generics.ListAPIView):
	queryset = AuthUser.objects.all().order_by('-date_joined')
	serializer_class = AuthUserSerializer
	permission_classes = [IsAuthenticated]


class SuppliersView(generics.ListAPIView):
	queryset = Supplier.objects.all().order_by('-date_create')
	serializer_class = SuppliersSerializer
	permission_classes = [IsAuthenticated]


