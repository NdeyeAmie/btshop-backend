from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_all_products, name='get-all-products'),
    path('featured/', views.get_featured_products, name='get-featured-products'),
    path('create/', views.create_product, name='create-product'),
    path('fragrances/', views.get_all_fragrances, name='get-all-fragrances'),
    path('<uuid:product_id>/', views.get_product_by_id, name='get-product-by-id'),
    path('<uuid:product_id>/update/', views.update_product, name='update-product'),
    path('<uuid:product_id>/delete/', views.delete_product_api, name='delete-product'),
    path('<uuid:product_id>/reviews/', views.add_review, name='add-review'),
    path('<uuid:product_id>/reviews/<uuid:review_id>/delete/', views.delete_review, name='delete-review'),
]