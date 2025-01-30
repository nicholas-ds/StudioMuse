import os
import anthropic

def call_llm(entry_text, rgb_colors):
    """
    Sends entry text and RGB colors to the Claude API using the anthropic library and retrieves the response.

    :param entry_text: The text from the physicalPaletteEntry GtkEntry widget.
    :param rgb_colors: A list of RGB tuples representing the selected palette colors.
    :return: The response from the Claude API.
    """
    try:
        # Initialize the Anthropic client
        client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_KEY")  # Defaults to the environment variable
        )

        # Create the prompt for Claude
        prompt = (
            f"Entry Text: {entry_text}\n"
            f"RGB Colors: {rgb_colors}\n"
            f"Please provide an analysis or recommendation based on the above data."
        )

        # Send the message to Claude
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",  # Use the appropriate model version
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Return the content of the message
        return message.content

    except Exception as e:
        return f"Error sending data to Claude: {e}"


        

# test_call_llm.py


def main():
    # Example entry text and RGB colors
    entry_text = "This is a test entry text."
    rgb_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]  # Example RGB tuples

    # Call the LLM function
    response = call_llm(entry_text, rgb_colors)

    # Print the response
    print("LLM Response:", response)

if __name__ == "__main__":
    main()

