from flask import Flask, render_template, request
import feedparser
import joblib
import os
from datetime import datetime  # Import datetime for timestamp

app = Flask(__name__)

# Load the saved model
model_path = os.path.join("model", "news_classifier_model.pkl")
model = joblib.load(model_path)

# RSS feed URLs
feed_urls = [
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://www.theguardian.com/rss",
    "https://apnews.com/index.rss",
    "https://asianews.network/feed/",
    "https://www.scmp.com/rss/feed"
]

def fetch_headlines(feed_urls):
    """Fetch headlines, summaries, and links from multiple RSS feeds."""
    headlines_with_details = []
    for url in feed_urls:
        feed = feedparser.parse(url)
        for entry in feed['entries']:
            headline = entry['title']
            summary = entry.get('summary', 'No summary available')  # Get summary if available
            link = entry.get('link', '#')  # Get link if available
            headlines_with_details.append((headline, summary, link))
    return headlines_with_details

@app.route("/", methods=["GET"])
def index():
    """Render the homepage with categorized news."""
    # Fetch real-time headlines, summaries, and links
    headlines_with_details = fetch_headlines(feed_urls)
    
    # Separate details, then classify headlines
    headlines = [item[0] for item in headlines_with_details]
    summaries = [item[1] for item in headlines_with_details]
    links = [item[2] for item in headlines_with_details]
    predicted_categories = model.predict(headlines)
    
    # Organize categorized news with summaries and links
    categorized_news = {}
    for headline, summary, link, category in zip(headlines, summaries, links, predicted_categories):
        if category not in categorized_news:
            categorized_news[category] = []  # Initialize category if it doesn't exist
        categorized_news[category].append((headline, summary, link))
    
    # Get the current timestamp
    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Return the rendered HTML template with news data and timestamp
    return render_template("index.html", news=categorized_news, last_updated=last_updated)

if __name__ == "__main__":
    app.run(debug=True)
