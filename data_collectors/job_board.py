"""
Job Board Monitor — Track hiring signals from competitor career pages.
Detects job postings that indicate product direction and team expansion.
"""

import requests
import time
import db
from bs4 import BeautifulSoup


def get_linkedin_company_jobs(company_name: str) -> list:
    """
    Get job postings for a company from LinkedIn public data.
    This uses basic web scraping of LinkedIn's public pages.
    Note: Requires respectful rate limiting.
    """
    try:
        # LinkedIn jobs URL (public, no auth required)
        url = f"https://www.linkedin.com/jobs/search?keywords={company_name}&geoId=92000000"

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        }

        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return []

        # Parse jobs from page (basic extraction)
        soup = BeautifulSoup(response.content, "html.parser")
        jobs = []

        # Find job listings (LinkedIn structure varies)
        job_cards = soup.find_all("div", {"class": "base-card"})[:5]  # Limit to 5

        for card in job_cards:
            try:
                title_elem = card.find("h3")
                title = title_elem.text.strip() if title_elem else "Unknown"

                company_elem = card.find("h4")
                company = company_elem.text.strip() if company_elem else ""

                jobs.append({
                    "title": title,
                    "company": company,
                    "description": f"Job posting for {title}"
                })
            except:
                continue

        return jobs

    except Exception as e:
        print(f"Error fetching LinkedIn jobs for {company_name}: {e}")
        return []


def analyze_hiring_signals(job_title: str) -> dict:
    """
    Analyze what a job title reveals about product direction.
    """
    job_lower = job_title.lower()

    areas = {
        "AI/ML": ["ai", "machine learning", "llm", "nlp", "deep learning", "neural"],
        "Platform": ["platform", "infrastructure", "devops", "backend", "api"],
        "Mobile": ["ios", "android", "mobile", "react native"],
        "Analytics": ["analytics", "data science", "bi", "metrics"],
        "Security": ["security", "privacy", "compliance", "infosec"]
    }

    detected_areas = []
    for area, keywords in areas.items():
        if any(keyword in job_lower for keyword in keywords):
            detected_areas.append(area)

    return {
        "focus_areas": detected_areas if detected_areas else ["General"],
        "hiring_signal": f"Expanding team in: {', '.join(detected_areas)}" if detected_areas else "General hiring"
    }


def monitor_job_boards():
    """
    Monitor job boards for hiring signals from competitors.
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

        try:
            # Get LinkedIn jobs
            jobs = get_linkedin_company_jobs(competitor["name"])

            for job in jobs:
                signals = analyze_hiring_signals(job["title"])

                content = f"""
Company: {competitor['name']}
Job Title: {job['title']}
Focus Areas: {', '.join(signals['focus_areas'])}
Signal: {signals['hiring_signal']}
"""

                # Store raw data
                data_id = db.log_raw_data(
                    competitor["id"],
                    "JOBS",
                    content,
                    detected_change=True
                )

                total_found += 1
                total_processed += 1

        except Exception as e:
            errors.append(f"Job board monitor error for {competitor['name']}: {str(e)}")
            print(f"Error monitoring jobs for {competitor['name']}: {e}")

    duration = time.time() - start_time

    # Log collection run
    db.log_collection_run(
        "job_board",
        items_found=total_found,
        items_processed=total_processed,
        errors="; ".join(errors) if errors else None,
        duration_seconds=duration
    )

    print(f"✓ Job board monitor: {total_found} job postings found ({duration:.1f}s)")
    return {"items_found": total_found, "items_processed": total_processed}


if __name__ == "__main__":
    monitor_job_boards()
