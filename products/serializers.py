from rest_framework import serializers
from .models import Product, Fragrance , Review



class FragranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fragrance
        fields = ['id', 'name']


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'username', 'rating', 'comment', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    fragrances = FragranceSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    img = serializers.SerializerMethodField()
    hover_img = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'img', 'hover_img', 'desc',
            'price', 'count_in_stock', 'rating', 'num_reviews',
            'genre', 'featured', 'fragrances', 'reviews',
            'avg_rating', 'created_at'
        ]

    def get_avg_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0

    def get_img(self, obj):
        if obj.img:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.img.url)
            return obj.img.url
        return None

    def get_hover_img(self, obj):
        if obj.hover_img:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.hover_img.url)
            return obj.hover_img.url
        return None