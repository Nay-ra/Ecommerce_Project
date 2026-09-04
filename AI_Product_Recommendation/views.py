from django.shortcuts import render
from .services import AIRecommendationEngine

def recommendation_view(request):
    user_prompt = (
        request.POST.get('prompt') or 
        request.POST.get('q') or 
        request.POST.get('query') or 
        request.GET.get('prompt') or 
        request.GET.get('q') or 
        request.GET.get('query') or 
        ''
    ).strip()

    if user_prompt:
        # Strict intent matching for specific searches (e.g., "tv", "laptop", "phone")
        products, explanation = AIRecommendationEngine.get_search_recommendations(user_prompt)
    else:
        # Default personalized view when page loads empty
        products, explanation = AIRecommendationEngine.get_user_personalized_recommendations(request.user)

    return render(request, 'AI_Product_Recommendation/recommendations.html', {
        'recommended_products': products,
        'ai_explanation': explanation,
        'user_prompt': user_prompt
    })


ai_recommendations_view = recommendation_view