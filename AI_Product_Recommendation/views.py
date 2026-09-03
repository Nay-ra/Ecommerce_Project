import os
from django.shortcuts import render
from Product_Management.models import Product
from groq import Groq

def recommendation_view(request):
    products = Product.objects.all()
    recommendations = []
    ai_analysis = ""

    # Get optional search/preference query from user
    user_query = request.GET.get('query', '')

    if user_query:
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            try:
                client = Groq(api_key=api_key)
                
                # Format product list for LLM context
                catalog = "\n".join([f"- {p.name}: {p.description} (${p.price})" for p in products])
                
                prompt = f"""You are an e-commerce AI shopping assistant. 
Based on the user's preference: "{user_query}"
Select the best matching products from this catalog:
{catalog}

Provide a friendly 2-3 sentence recommendation explaining why these items fit their needs."""

                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                )
                ai_analysis = completion.choices[0].message.content
            except Exception as e:
                ai_analysis = "Here are some recommended items from our catalog based on your interest."
        
        # Simple search match fallback
        recommendations = Product.objects.filter(name__icontains=user_query) | Product.objects.filter(description__icontains=user_query)

    return render(request, 'AI_Product_Recommendation/recommendations.html', {
        'recommendations': recommendations,
        'ai_analysis': ai_analysis,
        'user_query': user_query,
        'all_products': products[:4],  # Fallback preview items
    })