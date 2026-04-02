"""
RSS Parser — Monitor competitor blogs and RSS feeds.
Detects new blog posts, press releases, announcements.
"""

import feedparser
import time
import db


def parse_rss_feed(feed_url: str) -> list:
    """
    Parse an RSS feed and return entries.
    Returns list of dicts with title, description, link, published date.
    """
    try:
        feed = feedparser.parse(feed_url)
        entries = []

        for entry in feed.entries[:10]:  # Last 10 entries
            entries.append({
                "title": entry.get("title", ""),
                "description": entry.get("summary", "")[:200],
                "link": entry.get("link", ""),
                "published": entry.get("published", "")
            })

        return entries
    except Exception as e:
        print(f"Error parsing RSS {feed_url}: {e}")
        return []


def monitor_rss_feeds():
    """
    Monitor RSS feeds for all competitors.
    Detects new blog posts, announcements.
    """
    competitors = db.get_all_competitors()
    if not competitors:
        print("No competitors to monitor")
        return

    start_time = time.time()
    total_found = 0
    total_processed = 0
    errors = []

    for competitor in competitors:
        if competitor["status"] != "ACTIVE":
            continue

        # Get RSS sources for this competitor
        sources = db.get_sources_for_competitor(competitor["id"], active_only=True)
        rss_sources = [s for s in sources if s["source_type"] == "RSS"]

        for source in rss_sources:
            try:
                feed_url = source["source_url"]
                if not feed_url:
                    continue

                # Parse RSS feed
                entries = parse_rss_feed(feed_url)

                for entry in entries:
                    # Create content string
                    content = f"Title: {entry['title']}\n\nDescription: {entry['description']}\n\nLink: {entry['link']}"

                    # Store raw data
                    data_id = db.log_raw_data(
                        competitor["id"],
                        "RSS",
                        content,
                        detected_change=True
                    )

                    total_found += 1
                    total_processed += 1

            except Exception as e:
                errors.append(f"RSS parser error for {competitor['name']}: {str(e)}")
                print(f"Error parsing RSS for {competitor['name']}: {e}")

    duration = time.time() - start_time

    # Log collection run
    db.log_collection_run(
        "rss_parser",
        items_found=total_found,
        items_processed=total_processed,
        errors="; ".join(errors) if errors else None,
        duration_seconds=duration
    )

    print(f"✓ RSS parser: {total_found} posts found ({duration:.1f}s)")
    return {"items_found": total_found, "items_processed": total_processed}


if __name__ == "__main__":
    monitor_rss_feeds()
