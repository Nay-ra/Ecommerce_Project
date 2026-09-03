from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from Product_Management.models import Product
from .services import AIRecommendationEngine

def product_recommendations_api(request, product_id):
    """
    API endpoint returning JSON recommendations for dynamic UI widgets.
    """
    product = get_object_or_404(Product, id=product_id)
    similar_recs, similar_reason = AIRecommendationEngine.get_similar_products(product)
    trending_recs, trending_reason = AIRecommendationEngine.get_trending_products()

    data = {
        'similar': {
            'explanation': similar_reason,
            'products': [{'id': p.id, 'name': p.name, 'price': str(p.price), 'slug': p.slug} for p in similar_recs]
        },
        'trending': {
            'explanation': trending_reason,
            'products': [{'id': p.id, 'name': p.name, 'price': str(p.price), 'slug': p.slug} for p in trending_recs]
        }
    }
    return JsonResponse(data)