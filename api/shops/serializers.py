from rest_framework import serializers
from app.models import Shop, ShopScraper


class ShopSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    location = serializers.CharField(read_only=True)
    language = serializers.CharField(read_only=True)
    status = serializers.IntegerField(read_only=True)
    is_default = serializers.IntegerField(read_only=True)
    datetime_added = serializers.DateTimeField(format="%b %d, %Y - %H:%M %p", read_only=True)
    uploaded_by = serializers.CharField(source='uploaded_by.get_fullname_formatted')

    class Meta:
        model = Shop
        fields = '__all__'


class ScrapperSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    shop = serializers.CharField(source='shop.name')
    product_name_class = serializers.CharField(read_only=True)
    image_source = serializers.CharField(read_only=True)
    product_name_htype = serializers.CharField(read_only=True)
    shop_id = serializers.CharField(source='shop.id')

    class Meta:
        model = ShopScraper
        fields = ['id', 'shop', 'product_name_class', 'image_source', 'product_name_htype', 'shop_id',
            'manufacturer_htype', 'content_htype', 'stock_status_htype', 'price_htype', 'image_htype',
            'link_htype', 'wrapper_htype', 'manufacturer_class', 'content_class',
            'stock_status_class', 'price_class', 'image_class', 'link_class', 'wrapper_class']
