import uuid
from django.db import models


class Fragrance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    GENRE_CHOICES = (
        ('elle', 'Elle'),
        ('lui', 'Lui'),
        ('mixte', 'Mixte'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    img = models.ImageField(upload_to='products/', blank=True, null=True)
    hover_img = models.ImageField(upload_to='products/', blank=True, null=True)
    desc = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    count_in_stock = models.IntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    num_reviews = models.IntegerField(default=0)
    genre = models.CharField(max_length=10, choices=GENRE_CHOICES)
    featured = models.BooleanField(default=False)
    fragrances = models.ManyToManyField(Fragrance, blank=True, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    rating = models.IntegerField(default=1)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')  # un avis par user par produit

    def __str__(self):
        return f"{self.user.username} - {self.product.title} - {self.rating}/5"