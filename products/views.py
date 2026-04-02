from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Product, Fragrance, Review
from .serializers import ProductSerializer, FragranceSerializer, ReviewSerializer


class ProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


# ✅ GET tous les produits avec filtres + pagination
@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_products(request):
    products = Product.objects.all()

    # Filtres
    genre = request.query_params.get('genre')
    fragrance = request.query_params.get('fragrance')
    featured = request.query_params.get('featured')
    search = request.query_params.get('search')

    if genre:
        products = products.filter(genre=genre)
    if fragrance:
        products = products.filter(fragrances__name__icontains=fragrance)
    if featured:
        products = products.filter(featured=True)
    if search:
        products = products.filter(title__icontains=search)

    products = products.order_by('-created_at')

    # Pagination
    paginator = ProductPagination()
    result_page = paginator.paginate_queryset(products, request)
    serializer = ProductSerializer(result_page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


# ✅ GET produit par ID
@api_view(['GET'])
@permission_classes([AllowAny])
def get_product_by_id(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Produit non trouvé'}, status=404)
    return Response(ProductSerializer(product, context={'request': request}).data)


# ✅ GET produits featured
@api_view(['GET'])
@permission_classes([AllowAny])
def get_featured_products(request):
    products = Product.objects.filter(featured=True).order_by('-created_at')
    paginator = ProductPagination()
    result_page = paginator.paginate_queryset(products, request)
    serializer = ProductSerializer(result_page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


# ✅ CREATE produit
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_product(request):
    if request.user.role != 'admin':
        return Response({'error': 'Accès refusé'}, status=403)

    title = request.data.get('title')
    desc = request.data.get('desc')
    price = request.data.get('price')
    count_in_stock = request.data.get('count_in_stock')
    genre = request.data.get('genre')
    featured_value = request.data.get('featured', False)
    featured = featured_value in [True, 'true', 'True', '1', 1]
    img = request.FILES.get('img')
    hover_img = request.FILES.get('hover_img')
    fragrance_ids = request.data.getlist('fragrances') if hasattr(request.data, 'getlist') else request.data.get('fragrances', [])

    if not title or not price or not genre:
        return Response({'error': 'title, price et genre sont obligatoires'}, status=400)

    product = Product.objects.create(
        title=title, desc=desc, price=price,
        count_in_stock=count_in_stock, genre=genre,
        featured=featured, img=img, hover_img=hover_img,
    )
    if fragrance_ids:
        product.fragrances.set(fragrance_ids)

    return Response(ProductSerializer(product, context={'request': request}).data, status=201)


# ✅ UPDATE produit
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_product(request, product_id):
    if request.user.role != 'admin':
        return Response({'error': 'Accès refusé'}, status=403)
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Produit non trouvé'}, status=404)

    product.title = request.data.get('title', product.title)
    product.desc = request.data.get('desc', product.desc)
    product.price = request.data.get('price', product.price)
    product.count_in_stock = request.data.get('count_in_stock', product.count_in_stock)
    product.genre = request.data.get('genre', product.genre)
    featured_value = request.data.get('featured', product.featured)
    product.featured = featured_value in [True, 'true', 'True', '1', 1]

    if request.FILES.get('img'):
        product.img = request.FILES.get('img')
    if request.FILES.get('hover_img'):
        product.hover_img = request.FILES.get('hover_img')

    product.save()

    fragrance_ids = request.data.getlist('fragrances') if hasattr(request.data, 'getlist') else request.data.get('fragrances', [])
    if fragrance_ids:
        product.fragrances.set(fragrance_ids)

    return Response(ProductSerializer(product, context={'request': request}).data)


# ✅ DELETE produit
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_product_api(request, product_id):
    if request.user.role != 'admin':
        return Response({'error': 'Accès refusé'}, status=403)
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Produit non trouvé'}, status=404)
    product.delete()
    return Response({'message': 'Produit supprimé avec succès'}, status=200)


# ✅ GET toutes les fragrances
@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_fragrances(request):
    fragrances = Fragrance.objects.all()
    return Response(FragranceSerializer(fragrances, many=True).data)


# ✅ Ajouter un avis
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_review(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Produit non trouvé'}, status=404)

    if Review.objects.filter(product=product, user=request.user).exists():
        return Response({'error': 'Vous avez déjà donné un avis sur ce produit'}, status=400)

    rating = int(request.data.get('rating', 1))
    if rating < 1 or rating > 5:
        return Response({'error': 'La note doit être entre 1 et 5'}, status=400)

    comment = request.data.get('comment', '')

    review = Review.objects.create(
        product=product,
        user=request.user,
        rating=rating,
        comment=comment,
    )

    # Mettre à jour rating et num_reviews du produit
    all_reviews = Review.objects.filter(product=product)
    product.num_reviews = all_reviews.count()
    product.rating = round(sum(r.rating for r in all_reviews) / all_reviews.count(), 1)
    product.save()

    return Response(ReviewSerializer(review).data, status=201)


# ✅ Supprimer un avis
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_review(request, product_id, review_id):
    try:
        review = Review.objects.get(id=review_id, product_id=product_id, user=request.user)
    except Review.DoesNotExist:
        return Response({'error': 'Avis non trouvé'}, status=404)

    review.delete()

    # Mettre à jour rating et num_reviews
    product = Product.objects.get(id=product_id)
    all_reviews = Review.objects.filter(product=product)
    product.num_reviews = all_reviews.count()
    product.rating = round(sum(r.rating for r in all_reviews) / all_reviews.count(), 1) if all_reviews.exists() else 0
    product.save()

    return Response({'message': 'Avis supprimé'}, status=200)