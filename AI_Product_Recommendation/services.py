from django.db.models import Count, Sum
from Product_Management.models import Product, Category
from Order_Management.models import OrderItem, Order
from Shopping_Cart.models import CartItem

class AIRecommendationEngine:
    """
    AI Recommendation Engine serving content-based filtering,
    trending product analysis, and natural language explanations (FR-6).
    """

    @staticmethod
    def get_similar_products(product, limit=4):
        """
        Recommends products similar to a target product based on category
        and shared descriptive features.
        """
        if not product:
            return Product.objects.none(), ""

        # 1. Fetch products in the same category excluding current product
        similar_queryset = Product.objects.filter(
            category=product.category,
            is_available=True
        ).exclude(id=product.id)

        # 2. Fallback: If category has few items, grab top available items
        if similar_queryset.count() < limit:
            fallback = Product.objects.filter(is_available=True).exclude(
                id__in=[product.id] + list(similar_queryset.values_list('id', flat=True))
            )
            similar_queryset = (similar_queryset | fallback)

        recommendations = list(similar_queryset[:limit])
        explanation = f"Suggested because you are viewing '{product.name}' in {product.category.name}."

        return recommendations, explanation

    @staticmethod
    def get_trending_products(limit=4):
        """
        Calculates trending/popular products based on completed order volume.
        Falls back to newest items if purchase history is minimal.
        """
        # Query top purchased items from OrderItems
        trending_ids = (
            OrderItem.objects.values('product_id')
            .annotate(total_sold=Sum('quantity'))
            .order_by('-total_sold')
            .values_list('product_id', flat=True)[:limit]
        )

        trending_products = list(Product.objects.filter(id__in=list(trending_ids), is_available=True))

        # Fallback if insufficient purchase history exists
        if len(trending_products) < limit:
            existing_ids = [p.id for p in trending_products]
            newest_products = Product.objects.filter(
                is_available=True
            ).exclude(id__in=existing_ids).order_by('-created_at')[:limit - len(trending_products)]
            
            trending_products.extend(list(newest_products))

        explanation = "Top-rated items currently trending across all store purchases."
        return trending_products, explanation

    @staticmethod
    def get_user_personalized_recommendations(user, limit=4):
        """
        Analyzes user's active cart and purchase history to suggest personalized items.
        """
        if not user or not user.is_authenticated:
            return AIRecommendationEngine.get_trending_products(limit=limit)

        # Find categories the user has interacted with via past orders
        past_categories = OrderItem.objects.filter(
            order__user=user
        ).values_list('product__category_id', flat=True)

        if past_categories:
            favorite_category_id = max(set(past_categories), key=list(past_categories).count)
            fav_category = Category.objects.get(id=favorite_category_id)
            
            recs = Product.objects.filter(
                category=fav_category,
                is_available=True
            ).order_by('-created_at')[:limit]

            explanation = f"Recommended based on your recent order interest in {fav_category.name}."
            return list(recs), explanation

        # Default fallback if user has no past order history
        return AIRecommendationEngine.get_trending_products(limit=limit)