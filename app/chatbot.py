import os
import requests

# Global dictionary to store conversation histories for each user
CONVERSATION_HISTORY = {}

def chatai(user_id, user_message):
    """
    Interacts with the custom GPT API while maintaining conversation context.
    Formats the response in HTML for better readability.
    """
    api_url = "https://api.gpts.vin/v1/chat/completions"
    api_key = os.getenv("OPENAI_API_KEY")  # Load the API key from environment variables

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Initialize conversation history for the user if it doesn't exist
    if user_id not in CONVERSATION_HISTORY:
        CONVERSATION_HISTORY[user_id] = [
            {"role": "system", "content": (
                "You are a friendly and knowledgeable investment assistant specializing in the Malaysian investment landscape. "
                "Your goal is to help users identify legitimate investment opportunities and detect fraudulent platforms. "
                "Format your responses in HTML for clear readability. Use headings, bullet points, and short paragraphs."
            )}
        ]

    # Add the user's message to the conversation history
    CONVERSATION_HISTORY[user_id].append({"role": "user", "content": user_message})

    data = {
        "model": "gpt-4",
        "messages": CONVERSATION_HISTORY[user_id],  # Pass the entire conversation history
    }

    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()

        # Get the GPT response
        bot_message = response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response received.")

        # Add the bot's response to the conversation history
        CONVERSATION_HISTORY[user_id].append({"role": "assistant", "content": bot_message})

        return bot_message
    except requests.exceptions.RequestException as e:
        print(f"Error in chatai function: {e}")
        return "<p>Oh no, something went wrong. Mind giving it another shot?</p>"

