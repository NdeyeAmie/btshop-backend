
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Order, OrderItem
from .serializers import OrderSerializer
from products.models import Product

from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas
import openpyxl


# ✅ Créer une commande (user connecté)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    user = request.user
    data = request.data

    items = data.get('items', [])

    if not items:
        return Response({'error': 'Aucun produit dans la commande'}, status=400)

    order = Order.objects.create(
        user=user,
        full_name=data.get('full_name', ''),
        email=data.get('email', ''),
        phone=data.get('phone', ''),
        address=data.get('address', ''),
        city=data.get('city', ''),
        postal_code=data.get('postal_code', ''),
        country=data.get('country', 'Sénégal'),
        total_price=0,
    )

    total = 0
    for item in items:
        try:
            product = Product.objects.get(id=item['product_id'])
        except Product.DoesNotExist:
            order.delete()
            return Response({'error': f"Produit {item['product_id']} non trouvé"}, status=404)

        quantity = int(item.get('quantity', 1))
        price = product.price

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=price,
        )
        total += price * quantity

    order.total_price = total
    order.save()

    return Response(OrderSerializer(order, context={'request': request}).data, status=201)

# ✅ Mes commandes (user connecté)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return Response(OrderSerializer(orders, many=True, context={'request': request}).data)


# ✅ Détail commande
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response({'error': 'Commande non trouvée'}, status=404)
    return Response(OrderSerializer(order, context={'request': request}).data)
# ✅ Toutes les commandes (admin JWT)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_orders(request):
    if request.user.role != 'admin':
        return Response({'error': 'Accès refusé'}, status=403)
    orders = Order.objects.all().order_by('-created_at')
    return Response(OrderSerializer(orders, many=True, context={'request': request}).data)


# ✅ Modifier statut commande (admin JWT)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):
    if request.user.role != 'admin':
        return Response({'error': 'Accès refusé'}, status=403)
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Commande non trouvée'}, status=404)
    order.status = request.data.get('status', order.status)
    order.save()
    return Response(OrderSerializer(order, context={'request': request}).data)


# ✅ Export PDF
def export_orders_pdf(request):
    orders = Order.objects.all().order_by('-created_at')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="commandes.pdf"'

    p = pdf_canvas.Canvas(response, pagesize=A4)
    width, height = A4
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, height - 50, "Liste des Commandes - BT Shop")

    p.setFont("Helvetica", 10)
    y = height - 100
    p.drawString(30, y, "#")
    p.drawString(80, y, "Client")
    p.drawString(200, y, "Total")
    p.drawString(280, y, "Statut")
    p.drawString(380, y, "Date")
    y -= 20

    for order in orders:
        if y < 50:
            p.showPage()
            y = height - 50
        p.drawString(30, y, str(order.id)[:8])
        p.drawString(80, y, order.user.username)
        p.drawString(200, y, f"{order.total_price} FCFA")
        p.drawString(280, y, order.get_status_display())
        p.drawString(380, y, order.created_at.strftime('%d/%m/%Y'))
        y -= 20

    p.save()
    return response


# ✅ Export Excel
def export_orders_excel(request):
    orders = Order.objects.all().order_by('-created_at')
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Commandes"

    ws.append(['ID', 'Client', 'Email', 'Téléphone', 'Total (FCFA)', 'Statut', 'Adresse', 'Date'])

    for order in orders:
        ws.append([
            str(order.id),
            order.user.username,
            order.user.email,
            order.phone or '-',
            float(order.total_price),
            order.get_status_display(),
            order.shipping_address or '-',
            order.created_at.strftime('%d/%m/%Y %H:%M'),
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="commandes.xlsx"'
    wb.save(response)
    return response