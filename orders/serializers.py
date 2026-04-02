from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title', read_only=True)
    product_img = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_title', 'product_img', 'quantity', 'price', 'total']

    def get_product_img(self, obj):
        if obj.product.img:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.product.img.url)
            return obj.product.img.url
        return None

    def get_total(self, obj):
        return obj.get_total()


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'username', 'status', 'total_price',
            'full_name', 'email', 'phone',
            'address', 'city', 'postal_code', 'country',
            'items', 'created_at', 'updated_at'
        ]