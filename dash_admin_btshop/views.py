from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from products.models import Product, Fragrance
from accounts.models import CustomUser
from orders.models import Order
from django.db.models import Sum
from django.db.models.functions import TruncMonth
import json

def admin_login_view(request):
    error = None
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.role == 'admin':
            login(request, user)
            return redirect('dash_admin:dashboard')
        else:
            error = "Identifiants incorrects ou accès refusé"
    
    return render(request, 'pages/login.html', {'error': error})


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'admin':
            return redirect('dash_admin:login')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def dashboard(request):
    return render(request, 'index.html')


def admin_logout_view(request):
    logout(request)
    return redirect('dash_admin:login')

# ✅ Détail utilisateur
@admin_required
def user_detail(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return redirect('dash_admin:user_list')
    
    orders = user.orders.all().order_by('-created_at')
    
    return render(request, 'pages/user_detail.html', {
        'user_detail': user,
        'orders': orders,
    })


# ✅ Supprimer utilisateur
@admin_required
def user_delete(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        user.delete()
    except CustomUser.DoesNotExist:
        pass
    return redirect('dash_admin:user_list')


# ✅ Activer/Désactiver utilisateur
@admin_required
def user_toggle_status(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        user.is_active = not user.is_active
        user.save()
    except CustomUser.DoesNotExist:
        pass
    return redirect('dash_admin:user_list')

# ✅ Liste des produits
@admin_required
def product_list(request):
    products = Product.objects.all().order_by('-id')
    return render(request, 'pages/product_list.html', {'products': products})

# ✅ product_create
@admin_required
def product_create(request):
    error = None
    if request.method == 'POST':
        title = request.POST.get('title')
        desc = request.POST.get('desc')
        price = request.POST.get('price')
        count_in_stock = request.POST.get('count_in_stock')
        genre = request.POST.get('genre')
        featured = request.POST.get('featured') == 'on'
        fragrance_ids = request.POST.getlist('fragrances')
        img = request.FILES.get('img')
        hover_img = request.FILES.get('hover_img')

        product = Product.objects.create(
            title=title, img=img, hover_img=hover_img,
            desc=desc, price=price, count_in_stock=count_in_stock,
            genre=genre, featured=featured,
        )
        if fragrance_ids:
            product.fragrances.set(fragrance_ids)

        return redirect('dash_admin:product_list')

    return render(request, 'pages/product_create.html', {
        'error': error,
        'fragrances': Fragrance.objects.all(),
    })


# ✅ product_update
@admin_required
def product_update(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return redirect('dash_admin:product_list')

    if request.method == 'POST':
        product.title = request.POST.get('title')
        product.desc = request.POST.get('desc')
        product.price = request.POST.get('price')
        product.count_in_stock = request.POST.get('count_in_stock')
        product.genre = request.POST.get('genre')
        product.featured = request.POST.get('featured') == 'on'
        if request.FILES.get('img'):
            product.img = request.FILES.get('img')
        if request.FILES.get('hover_img'):
            product.hover_img = request.FILES.get('hover_img')
        product.save()
        product.fragrances.set(request.POST.getlist('fragrances'))
        return redirect('dash_admin:product_list')

    return render(request, 'pages/product_update.html', {
        'product': product,
        'fragrances': Fragrance.objects.all(),
        'selected_fragrances': list(product.fragrances.values_list('id', flat=True)),
    })

# ✅ Supprimer un produit
@admin_required
def product_delete(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        product.delete()
    except Product.DoesNotExist:
        pass
    return redirect('dash_admin:product_list')
   
# ✅ Détail produit dashboard
@admin_required
def product_detail(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return redirect('dash_admin:product_list')
    
    reviews = product.reviews.all().order_by('-created_at')
    
    return render(request, 'pages/product_detail.html', {
        'product': product,
        'reviews': reviews,
    })

# ✅ Liste fragrances
@admin_required
def fragrance_list(request):
    fragrances = Fragrance.objects.all().order_by('-id')
    error = None
    if request.method == 'POST':
        name = request.POST.get('name')
        if Fragrance.objects.filter(name=name).exists():
            error = "Cette fragrance existe déjà"
        else:
            Fragrance.objects.create(name=name)
            return redirect('dash_admin:fragrance_list')
    return render(request, 'pages/fragrance_list.html', {
        'fragrances': fragrances,
        'error': error,
        'suggestions': ['Oriental', 'Floral', 'Woody', 'Fresh', 'Citrus', 'Musky', 'Spicy', 'Aquatic'],
    })

# ✅ Supprimer fragrance
@admin_required
def fragrance_delete(request, fragrance_id):
    try:
        Fragrance.objects.get(id=fragrance_id).delete()
    except Fragrance.DoesNotExist:
        pass
    return redirect('dash_admin:fragrance_list')

# ✅ Liste des utilisateurs
@admin_required
def user_list(request):
    users = CustomUser.objects.all().exclude(username=request.user.username).order_by('-id')
    return render(request, 'pages/user_list.html', {'users': users})

# ✅ Liste des commandes
@admin_required
def order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'pages/order_list.html', {'orders': orders})


# ✅ Détail commande
@admin_required
def order_detail(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return redirect('dash_admin:order_list')
    return render(request, 'pages/order_detail.html', {'order': order})


# ✅ Modifier statut commande
@admin_required
def order_update_status(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return redirect('dash_admin:order_list')

    if request.method == 'POST':
        order.status = request.POST.get('status')
        order.save()

    return redirect('dash_admin:order_detail', order_id=order_id)

@admin_required
def dashboard(request):
    total_orders = Order.objects.count()
    total_products = Product.objects.count()
    total_users = CustomUser.objects.filter(role='user').count()
    total_revenue = Order.objects.filter(status='delivered').aggregate(
        total=Sum('total_price'))['total'] or 0

    pending = Order.objects.filter(status='pending').count()
    confirmed = Order.objects.filter(status='confirmed').count()
    shipped = Order.objects.filter(status='shipped').count()
    delivered = Order.objects.filter(status='delivered').count()
    cancelled = Order.objects.filter(status='cancelled').count()

    recent_orders = Order.objects.all().order_by('-created_at')[:5]
    recent_products = Product.objects.all().order_by('-created_at')[:5]

    # Ventes par mois
    monthly_sales = Order.objects.filter(
        status='delivered'
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        total=Sum('total_price')
    ).order_by('month')

    months_labels = [s['month'].strftime('%b %Y') for s in monthly_sales]
    months_data = [float(s['total']) for s in monthly_sales]

    return render(request, 'index.html', {
        'total_orders': total_orders,
        'total_products': total_products,
        'total_users': total_users,
        'total_revenue': total_revenue,
        'pending': pending,
        'confirmed': confirmed,
        'shipped': shipped,
        'delivered': delivered,
        'cancelled': cancelled,
        'recent_orders': recent_orders,
        'recent_products': recent_products,
        'months_labels': json.dumps(months_labels),
        'months_data': json.dumps(months_data),
    })