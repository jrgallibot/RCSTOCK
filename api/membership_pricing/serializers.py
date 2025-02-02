from rest_framework import serializers

from app.backend.models import Loghistory, TblMembershipPricing


class MembershipSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    uploaded_by = serializers.CharField(source='uploaded_by.get_fullname_formatted', read_only=True)

    class Meta:
        model = TblMembershipPricing
        fields = '__all__'
