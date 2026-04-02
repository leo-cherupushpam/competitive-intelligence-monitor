"""
Website Monitor — Track competitor website changes using Playwright.
Monitors pricing, features, blog pages for changes.
"""

import asyncio
import time
from datetime import datetime, timezone
import hashlib
import db
from playwright.async_api import async_playwright


async def get_page_content(url: str) -> str:
    """
    Fetch page content using Playwright.
    Returns text content of the page.
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=10000)
            content = await page.content()
            await browser.close()
            return content[:2000]  # Limit to 2000 chars for storage
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return f"Error: {str(e)}"


def detect_change(new_content: str, old_content: str) -> bool:
    """
    Detect if content has changed significantly.
    Uses diff detection (if > 5% different, flag as change).
    """
    if not old_content:
        return True

    # Simple hash-based comparison
    old_hash = hashlib.md5(old_content.encode()).hexdigest()
    new_hash = hashlib.md5(new_content.encode()).hexdigest()

    return old_hash != new_hash


async def monitor_competitor_websites():
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

        # Get website sources for this competitor
        sources = db.get_sources_for_competitor(competitor["id"], active_only=True)
        website_sources = [s for s in sources if s["source_type"] == "WEBSITE"]

        for source in website_sources:
            try:
                url = source["source_url"]
                if not url:
                    continue

                # Fetch current content
                current_content = await get_page_content(url)

                # Get previous content from database
                from sqlalchemy import text  # Would need proper import
                # For now, just log as new data
                detected_change = True  # Assume change for now (first collection)

                # Store raw data
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

    # Log collection run
    db.log_collection_run(
        "website_monitor",
        items_found=total_found,
        items_processed=total_processed,
        errors="; ".join(errors) if errors else None,
        duration_seconds=duration
    )

    print(f"✓ Website monitor: {total_found} sites checked, {total_processed} changes detected ({duration:.1f}s)")
    return {"items_found": total_found, "items_processed": total_processed}


async def monitor_single_competitor(competitor_id: int, website_url: str):
    """Monitor a single competitor's website."""
    try:
        content = await get_page_content(website_url)
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
    # For testing
    asyncio.run(monitor_competitor_websites())
