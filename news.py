import requests
import csv
import os
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()

# === CONFIGURATION ===
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

QUERY = "stocks OR stock market OR earnings OR CEO"  # Customize keywords
NUM_HEADLINES = 10
OUTPUT_FILE = "headlines.csv"

# === FUNCTION TO GET HEADLINES ===
def get_news_headlines(api_key, query, num_headlines):
    url = f"https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": num_headlines,
        "apiKey": api_key
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Error fetching news: {response.status_code}, {response.text}")

    data = response.json()
    headlines = []
    for article in data.get("articles", []):
        headline = article["title"]
        timestamp = article["publishedAt"]
        headlines.append((headline, timestamp))
    return headlines

# === FUNCTION TO SAVE HEADLINES TO CSV ===
def save_to_csv(headlines, filename):
    with open(filename, mode="a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        for headline, timestamp in headlines:
            writer.writerow([timestamp, headline])
    print(f"Saved {len(headlines)} headlines to {filename}")

# === MAIN ===
def main():
    print("Pulling stock-related news headlines...")
    headlines = get_news_headlines(NEWSAPI_KEY, QUERY, NUM_HEADLINES)
    save_to_csv(headlines, OUTPUT_FILE)

if __name__ == "__main__":
    main()
