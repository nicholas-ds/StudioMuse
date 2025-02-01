import os
import requests
# from prompts import palette_dm_prompt  # Unused import



def call_llm(entry_text):
    """
    Sends user-provided text describing their physical palette and RGB colors 
    extracted from GIMP color paletteto the Perplexity Sonar API and retrieves the response.

    :param entry_text: The text from the physicalPaletteEntry GtkEntry widget.
    :param rgb_colors: A list of RGB tuples representing the selected palette colors.
    :return: The response from the Perplexity Sonar API.
    """
    try:
        url = "https://api.perplexity.ai/chat/completions"
        
        # Create the prompt for Sonar
        #prompt = palette_dm_prompt  # Assuming this is a string or formatted string

        payload = {
            "model": "sonar",
            "messages": [
                {
                    "role": "system",
                    "content": """Act as an expert artist familiar with the Mont Marte 52 Extra Soft Vibrant oil pastel set. 
                    Provide: 
                    1. Direct color matches from the set for given RGB values 
                    2. Blending combinations for precise matches 
                    3. Application tips for oil pastels
                    """


                },
                {
                    "role": "user",
                    "content": entry_text
                }
            ],
            "max_tokens": 1024,
            "temperature": 0.2,
            "top_p": 0.9,
            "search_domain_filter": None,
            "return_images": False,
            "return_related_questions": False,
            "search_recency_filter": "month",
            "top_k": 0,
            "stream": False,
            "presence_penalty": 0,
            "frequency_penalty": 1,
            "response_format": None
        }

        headers = {
            "Authorization": f"Bearer {os.getenv('PERPLEXITY_KEY')}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)

        # Check if the request was successful
        response.raise_for_status()

        # Print the full response for debugging
        #print("Full Response:", response.json())

        # Extract the content from the response
        choices = response.json().get('choices', [])
        if choices:
            return choices[0].get('message', {}).get('content', 'No content returned')
        else:
            return 'No content returned'

    except Exception as e:
        return f"Error sending data to Sonar: {type(e).__name__}: {e}"


        

# test_call_llm.py
def main():
    # Example entry text and RGB colors
    rgb_colors = [(21, 52, 52)]  # Example RGB tuples
    entry_text = f"""Target RGB: {rgb_colors}
                Available colors: [List all Mont Marte colors here]
                Response format: JSON with 'direct_matches', 'blending_suggestions', 'usage_tips'"""

    # Call the LLM function
    response = call_llm(entry_text)

    # Print the response
    print("LLM Response:", response)

if __name__ == "__main__":
    main()

