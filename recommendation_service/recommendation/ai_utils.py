import requests

def generate_recommendation(new_farmers, products_posted):
    prompt = f"""
    Last week, {new_farmers} new farmers joined our portal,
    and {products_posted} products were posted on the e-commerce platform.

    Suggest 2-3 personalized tips to increase farmer engagement.
    """
    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/google/flan-t5-small",
            headers={"Authorization": "Bearer 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"},
            json={"inputs": prompt}
        )
        return response.json()[0]['generated_text']
    except:
        return "AI recommendation currently unavailable."
