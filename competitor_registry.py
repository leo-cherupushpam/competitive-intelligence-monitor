"""
Competitor Registry — Pre-built competitor libraries by market segment.
Helps users quickly set up competitors to track.
"""

COMPETITOR_LIBRARY = {
    "CRM": {
        "description": "Customer Relationship Management platforms",
        "competitors": [
            {
                "name": "HubSpot",
                "website": "https://www.hubspot.com",
                "threat_baseline": "HIGH",
                "rss_feed": "https://blog.hubspot.com/feed",
                "linkedin": "https://linkedin.com/company/hubspot"
            },
            {
                "name": "Salesforce",
                "website": "https://www.salesforce.com",
                "threat_baseline": "HIGH",
                "rss_feed": "https://www.salesforce.com/news/feed",
                "linkedin": "https://linkedin.com/company/salesforce"
            },
            {
                "name": "Pipedrive",
                "website": "https://www.pipedrive.com",
                "threat_baseline": "MEDIUM",
                "rss_feed": "https://blog.pipedrive.com/feed",
                "linkedin": "https://linkedin.com/company/pipedrive"
            },
            {
                "name": "Zoho CRM",
                "website": "https://www.zoho.com/crm",
                "threat_baseline": "MEDIUM",
                "rss_feed": "https://blog.zoho.com/category/crm/feed",
                "linkedin": "https://linkedin.com/company/zoho"
            },
            {
                "name": "Close",
                "website": "https://www.close.com",
                "threat_baseline": "MEDIUM",
                "rss_feed": "https://blog.close.com/feed",
                "linkedin": "https://linkedin.com/company/close-io"
            }
        ]
    },
    "Project Management": {
        "description": "Project and task management tools",
        "competitors": [
            {
                "name": "Asana",
                "website": "https://www.asana.com",
                "threat_baseline": "HIGH",
                "rss_feed": "https://blog.asana.com/feed",
                "linkedin": "https://linkedin.com/company/asana"
            },
            {
                "name": "Monday.com",
                "website": "https://www.monday.com",
                "threat_baseline": "HIGH",
                "rss_feed": "https://blog.monday.com/feed",
                "linkedin": "https://linkedin.com/company/monday-com"
            },
            {
                "name": "Jira",
                "website": "https://www.atlassian.com/software/jira",
                "threat_baseline": "HIGH",
                "rss_feed": "https://www.atlassian.com/feeds",
                "linkedin": "https://linkedin.com/company/atlassian"
            },
            {
                "name": "Linear",
                "website": "https://linear.app",
                "threat_baseline": "MEDIUM",
                "rss_feed": "https://linear.app/news/feed",
                "linkedin": "https://linkedin.com/company/linear-app"
            },
            {
                "name": "ClickUp",
                "website": "https://www.clickup.com",
                "threat_baseline": "MEDIUM",
                "rss_feed": "https://clickup.com/blog/feed",
                "linkedin": "https://linkedin.com/company/clickup"
            }
        ]
    },
    "Analytics": {
        "description": "Analytics, metrics, and BI platforms",
        "competitors": [
            {
                "name": "Mixpanel",
                "website": "https://www.mixpanel.com",
                "threat_baseline": "MEDIUM",
                "rss_feed": "https://mixpanel.com/blog/feed",
                "linkedin": "https://linkedin.com/company/mixpanel"
            },
            {
                "name": "Amplitude",
                "website": "https://www.amplitude.com",
                "threat_baseline": "MEDIUM",
                "rss_feed": "https://amplitude.com/blog/feed",
                "linkedin": "https://linkedin.com/company/amplitude-analytics"
            },
            {
                "name": "Heap",
                "website": "https://www.heap.io",
                "threat_baseline": "LOW",
                "rss_feed": "https://heap.io/blog/feed",
                "linkedin": "https://linkedin.com/company/heap-analytics"
            },
            {
                "name": "Segment",
                "website": "https://www.segment.com",
                "threat_baseline": "MEDIUM",
                "rss_feed": "https://segment.com/blog/feed",
                "linkedin": "https://linkedin.com/company/segment"
            }
        ]
    },
    "E-Commerce": {
        "description": "E-commerce and shopping platforms",
        "competitors": [
            {
                "name": "Shopify",
                "website": "https://www.shopify.com",
                "threat_baseline": "HIGH",
                "rss_feed": "https://www.shopify.com/blog/feed.xml",
                "linkedin": "https://linkedin.com/company/shopify"
            },
            {
                "name": "WooCommerce",
                "website": "https://www.woocommerce.com",
                "threat_baseline": "MEDIUM",
                "rss_feed": "https://www.woocommerce.com/blog/feed",
                "linkedin": "https://linkedin.com/company/woocommerce"
            },
            {
                "name": "BigCommerce",
                "website": "https://www.bigcommerce.com",
                "threat_baseline": "MEDIUM",
                "rss_feed": "https://blog.bigcommerce.com/feed",
                "linkedin": "https://linkedin.com/company/bigcommerce"
            }
        ]
    },
    "Developer Tools": {
        "description": "Developer tools and platforms",
        "competitors": [
            {
                "name": "GitHub",
                "website": "https://www.github.com",
                "threat_baseline": "HIGH",
                "rss_feed": "https://github.blog/feed",
                "linkedin": "https://linkedin.com/company/github"
            },
            {
                "name": "GitLab",
                "website": "https://www.gitlab.com",
                "threat_baseline": "MEDIUM",
                "rss_feed": "https://about.gitlab.com/blog/feed.xml",
                "linkedin": "https://linkedin.com/company/gitlab-com"
            },
            {
                "name": "Vercel",
                "website": "https://www.vercel.com",
                "threat_baseline": "MEDIUM",
                "rss_feed": "https://vercel.com/blog/feed.xml",
                "linkedin": "https://linkedin.com/company/vercel"
            }
        ]
    }
}


def get_competitors_for_segment(segment: str) -> list:
    """Get list of competitors for a market segment."""
    if segment not in COMPETITOR_LIBRARY:
        return []

    return COMPETITOR_LIBRARY[segment]["competitors"]


def get_all_segments() -> list:
    """Get list of all market segments."""
    return list(COMPETITOR_LIBRARY.keys())


def get_segment_description(segment: str) -> str:
    """Get description of a market segment."""
    if segment not in COMPETITOR_LIBRARY:
        return ""

    return COMPETITOR_LIBRARY[segment]["description"]


if __name__ == "__main__":
    # Test the registry
    print("Available Market Segments:")
    for segment in get_all_segments():
        print(f"\n{segment}:")
        print(f"  {get_segment_description(segment)}")
        competitors = get_competitors_for_segment(segment)
        print(f"  Competitors: {', '.join([c['name'] for c in competitors])}")
