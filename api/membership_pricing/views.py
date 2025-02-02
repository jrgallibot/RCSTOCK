from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from app.backend.models import Loghistory, TblMembershipPricing
from api.settings.serializers import LogsSerializer
from api.membership_pricing.serializers import MembershipSerializer


class MembershipPricingView(generics.ListAPIView):
	queryset = TblMembershipPricing.objects.all().order_by('-price')
	serializer_class = MembershipSerializer
	permission_classes = [IsAuthenticated]


