import os
import requests
# from prompts import palette_dm_prompt  # Unused import



def call_llm(entry_text):
    """
    Queries the Perplexity Sonar API to retrieve the Mont Marte pastel color list and match colors.
    """
    try:
        url = "https://api.perplexity.ai/chat/completions"

        payload = {
            "model": "sonar",  # Using the model that worked
            "messages": [
                {
                    "role": "user",
                    "content": f"""
                    Find the full color list for the Mont Marte 52 Extra Soft Vibrant Oil Pastel Set.
                    """
                }
            ],
            "top_k": 5,  # Keep it reasonable
        }

        headers = {
            "Authorization": f"Bearer {os.getenv('PERPLEXITY_KEY')}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        return response.json()

    except Exception as e:
        return f"Error sending data to Sonar: {type(e).__name__}: {e}"

def test_perplexity_web_search():
    """
    Tests if the Perplexity API key supports web search by querying for news headlines.

    :return: A JSON response indicating whether web search is enabled.
    """
    url = "https://api.perplexity.ai/chat/completions"

    payload = {
        "model": "sonar",  # Use "sonar" instead of "sonar-pro" for better search support
        "messages": [{"role": "user", "content": "Find the full color list for the Mont Marte 52 Extra Soft Vibrant Oil Pastel Set."}],
        "top_k": 5,  # Ensure web search is triggered
    }

    headers = {
        "Authorization": f"Bearer {os.getenv('PERPLEXITY_KEY')}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        # Check if response contains valid search results
        if "choices" in data and data["choices"]:
            print("✅ Web search is enabled for this API key.")
        else:
            print("❌ Web search is NOT enabled for this API key.")
        
        return data

    except requests.exceptions.RequestException as e:
        print(f"⚠️ API Request Failed: {e}")
        return None
        
# test_call_llm.py
def main():
    # Example entry text and RGB colors
    rgb_colors = [(33, 40, 39)]  # Example RGB tuples
    entry_text = f"""Target RGB: {rgb_colors}
                Available colors: [List all Mont Marte colors here]
                Response format: JSON with 'direct_matches', 'blending_suggestions', 'usage_tips'"""

    # Call the LLM function
    response = call_llm(entry_text)
    #response = test_perplexity_web_search()

    # Print the response
    print("LLM Response:", response)




if __name__ == "__main__":
    main()

