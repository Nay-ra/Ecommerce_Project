import json
import os
import re
from groq import Groq
from django.conf import settings
from django.db.models import Q, Sum
from Product_Management.models import Product, Category
from Order_Management.models import OrderItem


class AIRecommendationEngine:
    """
    AI Recommendation Engine serving content-based filtering,
    trending product analysis, user search intent matching, and Groq-powered natural language explanations (FR-6).
    """

    @staticmethod
    def _call_groq_api(system_prompt, context_str):
        """Helper to safely handle Groq API calls."""
        api_key = getattr(settings, 'GROQ_API_KEY', None) or os.environ.get("GROQ_API_KEY")
        if not api_key or api_key == "your-groq-api-key-here":
            return None

        try:
            client = Groq(api_key=api_key)
            completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context_str}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.0,  # Zero temperature ensures strictly deterministic matching
                response_format={"type": "json_object"}
            )
            return json.loads(completion.choices[0].message.content)
        except Exception:
            return None

    @staticmethod
    def get_search_recommendations(user_query, limit=4):
        """
        Matches explicit user text intent ("looking for a tv") strictly against catalog items.
        """
        if not user_query or not user_query.strip():
            return AIRecommendationEngine.get_trending_products(limit=limit)

        query_str = user_query.strip().lower()
        ignored_words = {
            'a', 'an', 'and', 'buy', 'find', 'for', 'give', 'i', 'looking',
            'me', 'need', 'of', 'please', 'recommend', 'show', 'the', 'want',
        }
        query_terms = [
            term for term in re.findall(r'[a-z0-9]+', query_str)
            if term not in ignored_words
        ]

        # 1. Fetch available store catalog
        catalog = list(Product.objects.filter(is_available=True).values('id', 'name', 'price', 'description'))
        if not catalog:
            return [], "No products currently available in the store."

        # Resolve direct catalog matches first so natural-language requests
        # cannot be broadened into unrelated recommendations by the model.
        direct_match = Q()
        for term in query_terms:
            direct_match |= (
                Q(name__icontains=term) |
                Q(description__icontains=term) |
                Q(category__name__icontains=term)
            )

        catalog_matches = list(
            Product.objects.filter(is_available=True).filter(direct_match).distinct()
        )
        if catalog_matches:
            return catalog_matches[:limit], f"Found {len(catalog_matches)} item(s) matching '{user_query}'."

        # 2. Strict AI prompt to prevent catalog leaks
        system_prompt = (
            "You are a strict E-Commerce Product Recommendation Assistant.\n"
            "RULES:\n"
            "1. Analyze the user's search query and compare it against the provided Store Catalog.\n"
            "2. ONLY return product IDs that explicitly match or directly relate to the user's intent.\n"
            "3. If the user asks for a 'laptop', return ONLY laptop IDs. DO NOT include phones, TVs, or unrelated products.\n"
            "4. NEVER return extra products to fill space. If only 1 product matches, return ONLY that 1 ID in `recommended_ids`.\n"
            "5. If NO products in the catalog match the user's query, return an empty array `[]` for `recommended_ids`.\n"
            "6. Provide a concise 1-sentence explanation for your choice.\n\n"
            "RESPONSE FORMAT (JSON ONLY):\n"
            '{\n  "recommended_ids": [1],\n  "explanation": "Selected the requested product from our store catalog."\n}'
        )

        context_str = f"Store Catalog: {json.dumps(catalog)}\nUser Search Query: \"{query_str}\""
        
        ai_result = AIRecommendationEngine._call_groq_api(system_prompt, context_str)

        if ai_result and "recommended_ids" in ai_result:
            rec_ids = ai_result.get("recommended_ids", [])
            explanation = ai_result.get("explanation", f"Recommendations matching '{user_query}'.")
            
            # Fetch products matched by AI while preserving order
            ai_products = [p for p in Product.objects.filter(id__in=rec_ids, is_available=True)]
            if ai_products:
                return ai_products[:limit], explanation

        # 3. Strict localized database fallback if Groq is unreachable
        return [], f"No matching products found for '{user_query}'."

    @staticmethod
    def get_similar_products(product, limit=4):
        """Recommends products in the exact same category without falling back to unrelated items."""
        if not product:
            return [], ""

        similar_queryset = Product.objects.filter(
            category=product.category,
            is_available=True
        ).exclude(id=product.id)[:limit]

        recommendations = list(similar_queryset)
        explanation = f"Suggested because you are viewing '{product.name}' in {product.category.name}."

        return recommendations, explanation

    @staticmethod
    def get_trending_products(limit=4):
        """Calculates trending products based on completed order volume."""
        trending_ids = (
            OrderItem.objects.values('product_id')
            .annotate(total_sold=Sum('quantity'))
            .order_by('-total_sold')
            .values_list('product_id', flat=True)[:limit]
        )

        trending_products = list(Product.objects.filter(id__in=list(trending_ids), is_available=True))

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
        """Analyzes past order categories to suggest relevant items."""
        if not user or not user.is_authenticated:
            return AIRecommendationEngine.get_trending_products(limit=limit)

        past_categories = list(OrderItem.objects.filter(
            order__user=user
        ).values_list('product__category_id', flat=True))

        if past_categories:
            favorite_category_id = max(set(past_categories), key=past_categories.count)
            fav_category = Category.objects.filter(id=favorite_category_id).first()
            
            if fav_category:
                recs = Product.objects.filter(
                    category=fav_category,
                    is_available=True
                ).order_by('-created_at')[:limit]

                explanation = f"Recommended based on your recent order interest in {fav_category.name}."
                return list(recs), explanation

        return AIRecommendationEngine.get_trending_products(limit=limit)