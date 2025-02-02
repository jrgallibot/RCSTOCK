from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from app.models import Shop, ShopScraper

from api.shops.serializers import ShopSerializer, ScrapperSerializer


class ShopView(generics.ListAPIView):
	queryset = Shop.objects.all().order_by('-datetime_added')
	serializer_class = ShopSerializer
	permission_classes = [IsAuthenticated]


class ScrappperView(generics.ListAPIView):
	queryset = ShopScraper.objects.all()
	serializer_class = ScrapperSerializer
	permission_classes = [IsAuthenticated]