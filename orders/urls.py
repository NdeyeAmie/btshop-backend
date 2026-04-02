from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_order, name='create-order'),
    path('my-orders/', views.my_orders, name='my-orders'),
    path('all/', views.get_all_orders, name='all-orders'),
    path('<uuid:order_id>/', views.order_detail, name='order-detail'),
    path('<uuid:order_id>/update-status/', views.update_order_status, name='update-order-status'),
    path('export/pdf/', views.export_orders_pdf, name='export-pdf'),
    path('export/excel/', views.export_orders_excel, name='export-excel'),
]