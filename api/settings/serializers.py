from rest_framework import serializers

from app.backend.models import Loghistory


class LogsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    descriptions = serializers.CharField(read_only=True)
    user = serializers.CharField(source='user.get_fullname_formatted', read_only=True)
    datetime_added = serializers.DateTimeField(format="%b %d, %Y - %H:%M %p", read_only=True)

    class Meta:
        model = Loghistory
        fields = ['id', 'descriptions', 'user', 'datetime_added']
