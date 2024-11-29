import requests
import json

# Replace with your actual News API key
API_KEY = "9a7471d7b0cb487a888503014f2c6843"

# Construct API URL with query and country specification
API_URL = f"https://newsapi.org/v2/everything?q=investment OR fraud OR scam&language=en&apiKey={API_KEY}"

def fetch_latest_news():
    try:
        response = requests.get(API_URL)
        print(f"Request URL: {API_URL}")
        print(f"Response Status Code: {response.status_code}")

        if response.status_code == 200:
            news_data = response.json()
            print(f"News Data Received: {news_data}")

            if 'articles' in news_data and len(news_data['articles']) > 0:
                # Save news data locally
                with open("latest_news.json", "w") as f:
                    json.dump(news_data, f, indent=4)  # Save with indent for better readability
                print("News updated successfully!")
            else:
                print("No articles found in the response.")
        else:
            print(f"Failed to fetch news. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching news: {e}")

if __name__ == "__main__":
    fetch_latest_news()
