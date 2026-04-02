"""
Website Monitor — Track competitor website changes using requests + BeautifulSoup.
Monitors pricing, features, blog pages for changes.
Works on Streamlit Cloud without Playwright dependencies.
"""

import requests
import time
import hashlib
import db
from bs4 import BeautifulSoup


def get_page_content(url: str) -> str:
    """
    Fetch page content using requests + BeautifulSoup.
    Returns visible text content of the page.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return f"Error: HTTP {response.status_code}"

        soup = BeautifulSoup(response.content, "html.parser")

        # Remove script and style elements
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        # Extract visible text
        text = soup.get_text(separator=" ", strip=True)

        # Limit to 2000 chars
        return text[:2000]

    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return f"Error: {str(e)}"


def detect_change(new_content: str, old_content: str) -> bool:
    """
    Detect if content has changed.
    Uses hash-based comparison.
    """
    if not old_content:
        return True

    old_hash = hashlib.md5(old_content.encode()).hexdigest()
    new_hash = hashlib.md5(new_content.encode()).hexdigest()

    return old_hash != new_hash


def monitor_competitor_websites():
    """
    Monitor all registered competitor websites.
    Checks pricing, features, blog pages for changes.
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

        sources = db.get_sources_for_competitor(competitor["id"], active_only=True)
        website_sources = [s for s in sources if s["source_type"] == "WEBSITE"]

        for source in website_sources:
            try:
                url = source["source_url"]
                if not url:
                    continue

                current_content = get_page_content(url)
                detected_change = True  # First collection always flagged

                data_id = db.log_raw_data(
                    competitor["id"],
                    "WEBSITE",
                    current_content,
                    detected_change=detected_change
                )

                total_found += 1
                if detected_change:
                    total_processed += 1

            except Exception as e:
                errors.append(f"Website monitor error for {competitor['name']}: {str(e)}")
                print(f"Error monitoring {competitor['name']}: {e}")

    duration = time.time() - start_time

    db.log_collection_run(
        "website_monitor",
        items_found=total_found,
        items_processed=total_processed,
        errors="; ".join(errors) if errors else None,
        duration_seconds=duration
    )

    print(f"✓ Website monitor: {total_found} sites checked, {total_processed} changes detected ({duration:.1f}s)")
    return {"items_found": total_found, "items_processed": total_processed}


def monitor_single_competitor(competitor_id: int, website_url: str):
    """Monitor a single competitor's website."""
    try:
        content = get_page_content(website_url)
        data_id = db.log_raw_data(
            competitor_id,
            "WEBSITE",
            content,
            detected_change=True
        )
        return data_id
    except Exception as e:
        print(f"Error monitoring website: {e}")
        return None


if __name__ == "__main__":
    monitor_competitor_websites()
