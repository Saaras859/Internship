# app.py
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
import requests
import os
from dotenv import load_dotenv
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

# Download required NLTK data
nltk.download('vader_lexicon')

# Initialize Flask app
app = Flask(__name__)

# Load environment variables
load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
QUERY = "stocks OR stock market OR earnings OR CEO"
NUM_HEADLINES = 10

# Initialize sentiment analyzer
sia = SentimentIntensityAnalyzer()

# Database setup
def init_db():
    conn = sqlite3.connect('trading.db')
    c = conn.cursor()
    
    # Create tables if they don't exist
    c.execute('''CREATE TABLE IF NOT EXISTS headlines
                 (id INTEGER PRIMARY KEY, 
                 timestamp TEXT, 
                 headline TEXT, 
                 sentiment REAL,
                 batch_id TEXT)''')
                 
    c.execute('''CREATE TABLE IF NOT EXISTS trades
                 (id INTEGER PRIMARY KEY,
                 batch_id TEXT,
                 timestamp TEXT,
                 avg_sentiment REAL,
                 decision TEXT)''')
                 
    conn.commit()
    conn.close()

# Fetch news headlines
def get_news_headlines():
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": QUERY,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": NUM_HEADLINES,
        "apiKey": NEWSAPI_KEY
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Error fetching news: {response.status_code}, {response.text}")
    
    data = response.json()
    return [(article["title"], article["publishedAt"]) for article in data.get("articles", [])]

# Analyze sentiment
def analyze_sentiment(headline):
    return sia.polarity_scores(headline)['compound']

# Make trading decision
def make_trading_decision(avg_sentiment):
    if avg_sentiment > 0.1:
        return "BUY"
    elif avg_sentiment < -0.1:
        return "SELL"
    return "HOLD"

# Save to database
def save_to_db(headlines, avg_sentiment, decision, batch_id):
    conn = sqlite3.connect('trading.db')
    c = conn.cursor()
    
    # Save headlines
    for headline, timestamp in headlines:
        sentiment = analyze_sentiment(headline)
        c.execute("INSERT INTO headlines (timestamp, headline, sentiment, batch_id) VALUES (?, ?, ?, ?)",
                 (timestamp, headline, sentiment, batch_id))
    
    # Save trade decision
    trade_time = datetime.utcnow().isoformat()
    c.execute("INSERT INTO trades (batch_id, timestamp, avg_sentiment, decision) VALUES (?, ?, ?, ?)",
             (batch_id, trade_time, avg_sentiment, decision))
    
    conn.commit()
    conn.close()

# Get data for visualization
def get_visualization_data():
    conn = sqlite3.connect('trading.db')
    c = conn.cursor()
    
    # Get latest headlines
    c.execute("SELECT timestamp, headline, sentiment FROM headlines ORDER BY timestamp DESC LIMIT 20")
    headlines = [{
        'timestamp': row[0],
        'headline': row[1],
        'sentiment': row[2]
    } for row in c.fetchall()]
    
    # Get trade history
    c.execute("SELECT timestamp, avg_sentiment, decision FROM trades ORDER BY timestamp DESC LIMIT 10")
    trades = [{
        'timestamp': row[0],
        'sentiment': row[1],
        'decision': row[2]
    } for row in c.fetchall()]
    
    # Get sentiment distribution
    c.execute("SELECT decision, COUNT(*) FROM trades GROUP BY decision")
    decision_dist = {row[0]: row[1] for row in c.fetchall()}
    
    conn.close()
    
    return headlines, trades, decision_dist

# Flask routes
@app.route('/')
def index():
    headlines, trades, decision_dist = get_visualization_data()
    return render_template('index.html', 
                           headlines=headlines,
                           trades=trades,
                           decision_dist=decision_dist)

@app.route('/fetch', methods=['POST'])
def fetch_news():
    try:
        headlines = get_news_headlines()
        if not headlines:
            return "No headlines found", 400
        
        # Calculate average sentiment
        sentiments = [analyze_sentiment(h[0]) for h in headlines]
        avg_sentiment = sum(sentiments) / len(sentiments)
        
        # Make trading decision
        decision = make_trading_decision(avg_sentiment)
        
        # Save with batch ID
        batch_id = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        save_to_db(headlines, avg_sentiment, decision, batch_id)
        
        return redirect(url_for('index'))
    
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True)