"""
News Monitor — Track competitor news from NewsAPI.
Detects M&A, funding, partnerships, leadership changes, major announcements.
Uses NewsAPI.org free tier (1,000 requests/month).
"""

import requests
import time
import db
from datetime import datetime, timedelta
from intelligence_engine import get_secret


def search_news(query: str, api_key: str = None) -> list:
    """
    Search news for a competitor using NewsAPI free tier.
    Returns list of news articles matching query.
    Note: Free tier limited to 1,000 requests/month.
    """
    if not api_key:
        # No API key available, graceful failure
        return []

    try:
        base_url = "https://newsapi.org/v2/everything"

        # Search for competitor name in news
        params = {
            "q": query,
            "sortBy": "publishedAt",
            "language": "en",
            "pageSize": 10,  # Get last 10 articles
            "apiKey": api_key
        }

        response = requests.get(base_url, params=params, timeout=10)

        if response.status_code != 200:
            return []

        data = response.json()
        articles = data.get("articles", [])

        articles_list = []
        for article in articles[:10]:
            articles_list.append({
                "title": article.get("title", ""),
                "description": article.get("description", "")[:200],
                "url": article.get("url", ""),
                "source": article.get("source", {}).get("name", ""),
                "published_at": article.get("publishedAt", ""),
                "content": article.get("content", "")[:100]
            })

        return articles_list

    except Exception as e:
        print(f"Error searching news for {query}: {e}")
        return []


def analyze_news_signal(article_title: str, article_description: str = "") -> dict:
    """
    Analyze what a news article reveals about competitive moves.
    Detects: M&A, funding, partnerships, leadership, major announcements.
    """
    full_text = (article_title + " " + article_description).lower()

    signals = {
        "M&A": ["acquired", "acquisition", "merged", "merger", "purchased", "buyout", "combination"],
        "Funding": ["funding", "raised", "series a", "series b", "series c", "ipo", "valuation", "investment"],
        "Partnership": ["partnership", "partners with", "announced partnership", "integrates with", "collaboration"],
        "Leadership": ["ceo", "cto", "appointed", "joins", "founder", "leadership", "hire", "new executive"],
        "Expansion": ["expanded", "expansion", "new market", "new region", "geographic", "enters market"],
        "Feature": ["launched", "release", "new product", "feature", "announced", "introduced"]
    }

    detected_signals = []
    for signal_type, keywords in signals.items():
        if any(keyword in full_text for keyword in keywords):
            detected_signals.append(signal_type)

    return {
        "signal_types": detected_signals if detected_signals else ["General News"],
        "news_signal": f"News: {', '.join(detected_signals)}" if detected_signals else "General competitor news"
    }


def monitor_news(api_key: str = None):
    """
    Monitor news for all competitors using NewsAPI.org free tier.
    Detects M&A, funding, partnerships, leadership changes.
    """
    competitors = db.get_all_competitors()
    if not competitors:
        print("No competitors to monitor")
        return

    if not api_key:
        print("NewsAPI key not configured, skipping news monitoring")
        return

    start_time = time.time()
    total_found = 0
    total_processed = 0
    errors = []

    for competitor in competitors:
        if competitor["status"] != "ACTIVE":
            continue

        try:
            # Search for news about this competitor
            articles = search_news(competitor["name"], api_key)

            for article in articles:
                signals = analyze_news_signal(article["title"], article["description"])

                content = f"""
Competitor: {competitor['name']}
Title: {article['title']}
Description: {article['description']}
Source: {article['source']}
Published: {article['published_at']}
URL: {article['url']}
Signal Types: {', '.join(signals['signal_types'])}
Analysis: {signals['news_signal']}
"""

                # Store raw data
                data_id = db.log_raw_data(
                    competitor["id"],
                    "NEWS",
                    content,
                    detected_change=True
                )

                total_found += 1
                total_processed += 1

        except Exception as e:
            errors.append(f"News monitor error for {competitor['name']}: {str(e)}")
            print(f"Error monitoring news for {competitor['name']}: {e}")

    duration = time.time() - start_time

    # Log collection run
    db.log_collection_run(
        "news_monitor",
        items_found=total_found,
        items_processed=total_processed,
        errors="; ".join(errors) if errors else None,
        duration_seconds=duration
    )

    print(f"✓ News monitor: {total_found} articles found ({duration:.1f}s)")
    return {"items_found": total_found, "items_processed": total_processed}


if __name__ == "__main__":
    monitor_news(get_secret("NEWSAPI_KEY"))
