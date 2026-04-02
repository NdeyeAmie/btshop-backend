from django.contrib import admin
from .models import Product, Fragrance

@admin.register(Fragrance)
class FragranceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'price', 'genre', 'featured', 'count_in_stock']