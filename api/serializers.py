from rest_framework import serializers

from app.backend.models import TblFaq, TblContactUs

class FaqSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    created_by = serializers.CharField(source='created_by.get_fullname_formatted', read_only=True)

    class Meta:
        model = TblFaq
        fields = '__all__'

class QueriesSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    date_added = serializers.DateTimeField(format="%b %d, %Y - %H:%M %p", read_only=True)
    class Meta:
        model = TblContactUs
        fields = '__all__'
