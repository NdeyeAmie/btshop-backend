from django.urls import path
from . import views

app_name = 'dash_admin'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.admin_login_view, name='login'),
    path('logout/', views.admin_logout_view, name='logout'),
    path('users/<uuid:user_id>/', views.user_detail, name='user_detail'),
    path('users/<uuid:user_id>/delete/', views.user_delete, name='user_delete'),
    path('users/<uuid:user_id>/toggle-status/', views.user_toggle_status, name='user_toggle_status'),

    # Produits
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<uuid:product_id>/update/', views.product_update, name='product_update'),
    path('products/<uuid:product_id>/delete/', views.product_delete, name='product_delete'),
    path('products/<uuid:product_id>/', views.product_detail, name='product_detail'),

    # Fragrances
    path('fragrances/', views.fragrance_list, name='fragrance_list'),
    path('fragrances/<uuid:fragrance_id>/delete/', views.fragrance_delete, name='fragrance_delete'),

    # Commandes
    path('orders/', views.order_list, name='order_list'),
    path('orders/<uuid:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<uuid:order_id>/update-status/', views.order_update_status, name='order_update_status'),

    # Utilisateurs
    path('users/', views.user_list, name='user_list'),
]