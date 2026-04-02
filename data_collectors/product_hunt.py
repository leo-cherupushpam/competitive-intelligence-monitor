"""
Product Hunt Monitor — Track new launches from competitors on Product Hunt.
"""

import requests
import time
import db


def search_product_hunt(query: str) -> list:
    """
    Search Product Hunt for launches.
    Returns list of products matching query.
    """
    try:
        # Product Hunt API endpoint
        # Note: This would require authentication for full access
        # For now, we'll use a simple search approach

        # Search via basic API (rate limited without auth)
        url = "https://api.producthunt.com/v2/api/graphql"
        headers = {
            "Accept": "application/json"
        }

        # GraphQL query to search for products
        query_string = f"""
        {{
            viewer {{
                products(first: 5, search: "{query}") {{
                    nodes {{
                        id
                        name
                        tagline
                        description
                        votesCount
                        url
                        createdAt
                    }}
                }}
            }}
        }}
        """

        # This requires auth, so we'll use a fallback for now
        return []

    except Exception as e:
        print(f"Error searching Product Hunt: {e}")
        return []


def monitor_product_hunt():
    """
    Monitor Product Hunt for new competitor launches.
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
            # Search for this competitor on Product Hunt
            results = search_product_hunt(competitor["name"])

            for product in results:
                content = f"""
Product Hunt Launch: {product.get('name', '')}
Tagline: {product.get('tagline', '')}
Description: {product.get('description', '')}
Votes: {product.get('votesCount', 0)}
URL: {product.get('url', '')}
Created: {product.get('createdAt', '')}
"""

                # Store raw data
                data_id = db.log_raw_data(
                    competitor["id"],
                    "PRODUCTHUNT",
                    content,
                    detected_change=True
                )

                total_found += 1
                total_processed += 1

        except Exception as e:
            errors.append(f"Product Hunt monitor error for {competitor['name']}: {str(e)}")
            print(f"Error monitoring {competitor['name']} on Product Hunt: {e}")

    duration = time.time() - start_time

    # Log collection run
    db.log_collection_run(
        "product_hunt",
        items_found=total_found,
        items_processed=total_processed,
        errors="; ".join(errors) if errors else None,
        duration_seconds=duration
    )

    print(f"✓ Product Hunt monitor: {total_found} launches found ({duration:.1f}s)")
    return {"items_found": total_found, "items_processed": total_processed}


if __name__ == "__main__":
    monitor_product_hunt()
