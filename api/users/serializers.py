from rest_framework import serializers

from app.backend.models import Supplier
from app.models import AuthUser


class AuthUserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    fullname = serializers.CharField(source='get_fullname_formatted', read_only=True)
    email = serializers.CharField(read_only=True)
    is_active = serializers.IntegerField(read_only=True)
    date_joined = serializers.DateTimeField(format="%b %d, %Y - %H:%M %p", read_only=True)
    permission = serializers.CharField(source='get_permission', read_only=True)

    class Meta:
        model = AuthUser
        fields = ['id', 'username', 'fullname', 'email', 'date_joined', 'is_active', 'permission']


class SuppliersSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    company_name = serializers.CharField(read_only=True)
    contact = serializers.CharField(read_only=True)
    address = serializers.CharField(read_only=True)
    phone = serializers.CharField(read_only=True)
    fax = serializers.CharField(read_only=True)
    home_page = serializers.CharField(read_only=True)
    status = serializers.IntegerField(read_only=True)
    date_create = serializers.DateTimeField(format="%b %d, %Y - %H:%M %p", read_only=True)

    class Meta:
        model = Supplier
        fields = ['id', 'company_name', 'contact', 'address', 'phone', 'fax',
        'home_page', 'status', 'date_create']
