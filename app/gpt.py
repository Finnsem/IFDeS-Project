import os
from dotenv import load_dotenv
import requests
import re

import requests

API_KEY = "9a7471d7b0cb487a888503014f2c6843"
url = f"https://newsapi.org/v2/top-headlines?country=my&category=business&apiKey={API_KEY}"

response = requests.get(url)
if response.status_code == 200:
    news_data = response.json()
    print(news_data)
else:
    print(f"Error: {response.status_code}")


# Load environment variables from .env file
load_dotenv()

def send_chatgpt_request(prompt, api_key, api_url):
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': 'gpt-4o',
            'messages': [{'role': 'user', 'content': prompt}]
        }

        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()  # Raise an error for bad HTTP status
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None

def format_as_html(content):
    """Format content into HTML by replacing markdown and formatting elements."""
    # Replace Markdown-style headings with HTML tags
    content = re.sub(r'######\s*(.+)', r'<h6>\1</h6>', content)
    content = re.sub(r'#####\s*(.+)', r'<h5>\1</h5>', content)
    content = re.sub(r'####\s*(.+)', r'<h4>\1</h4>', content)
    content = re.sub(r'###\s*(.+)', r'<h3>\1</h3>', content)
    content = re.sub(r'##\s*(.+)', r'<h2>\1</h2>', content)
    content = re.sub(r'#\s*(.+)', r'<h1>\1</h1>', content)

    # Replace bold, italic, and special formatting
    content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
    content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', content)
    content = content.replace("•", "<br>")

    # Handle bullet points and wrap in unordered list
    content = re.sub(r'(?:^|\n)-\s*(.+)', r'<li>\1</li>', content)
    content = re.sub(r'(<li>.*?</li>)', r'<ul>\1</ul>', content, flags=re.DOTALL)

    # Wrap paragraphs with <p> tags
    content = content.replace('\n\n', '</p><p>')
    content = f'<p>{content}</p>'

    return content

def determine_flag_color(content):
    """Determine the flag color based on the content."""
    if "high risk" in content.lower():
        return "red"
    elif "caution" in content.lower():
        return "yellow"
    return "green"

def gpt_generate_additional_info(base_response):
    api_url = "https://api.gpts.vin/v1/chat/completions"
    api_key = os.getenv("OPENAI_API_KEY")
    prompt = f"{base_response} Please provide a well-structured analysis, using headings, paragraphs, and bullet points where necessary."

    try:
        response = send_chatgpt_request(prompt, api_key, api_url)
        if not response:
            return f"{base_response} (An error occurred while generating additional AI content)"

        # Extract GPT response
        additional_info = response.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
        if not additional_info:
            return f"{base_response} (An error occurred while processing GPT response)"

        # Determine flag color and format content
        flag_color = determine_flag_color(additional_info)
        formatted_info = format_as_html(additional_info)

        # Add the flag color image
        flag_image_html = f'<img src="/static/images/{flag_color}_flag.png" alt="{flag_color} flag" style="width:50px;height:50px;">'

        return f"{base_response}{flag_image_html}{formatted_info}"

    except Exception as e:
        print(f"Error in gpt_generate_additional_info: {e}")
        return f"{base_response} (An error occurred while generating additional AI content: {e})"
