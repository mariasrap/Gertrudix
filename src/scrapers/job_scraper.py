"""
Job scraper for 80000hours.org using Algolia API

Filters applied:
- Areas: All EXCEPT Building Effective Altruism, Global Priorities Research, Policy & Government
- Location: USA and Remote/Global only
- Date: Only jobs posted since last scrape
"""

import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict

# Algolia API configuration (public search credentials from 80000hours.org)
ALGOLIA_APP_ID = "W6KM1UDIB3"
ALGOLIA_API_KEY = "d1d7f2c8696e7b36837d5ed337c4a319"
ALGOLIA_INDEX = "jobs_prod"

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "scraped_jobs"
RAW_DIR = DATA_DIR / "raw"
LAST_SCRAPE_FILE = DATA_DIR / "last_scrape.json"

# Problem areas to EXCLUDE
EXCLUDED_AREAS = [
    "Building effective altruism",
    "Global priorities research",
    "Improving institutional decision-making",  # Often policy-focused
]

# Location filters - include these
INCLUDED_LOCATIONS = [
    "USA",
    "Remote",
    "Global",
    "United States",
    "San Francisco",
    "New York",
    "Boston",
    "Seattle",
    "Los Angeles",
    "Bay Area",
]


def ensure_dirs():
    """Create necessary directories."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)


def get_last_scrape_date() -> Optional[datetime]:
    """Get the date of the last scrape."""
    if LAST_SCRAPE_FILE.exists():
        data = json.loads(LAST_SCRAPE_FILE.read_text())
        return datetime.fromisoformat(data.get("last_scrape"))
    return None


def save_last_scrape_date():
    """Save current date as last scrape date."""
    LAST_SCRAPE_FILE.write_text(json.dumps({
        "last_scrape": datetime.now().isoformat(),
        "source": "80000hours.org"
    }, indent=2))


def search_algolia(filters: str = "", hits_per_page: int = 1000) -> List[Dict]:
    """Query Algolia API for jobs."""
    url = f"https://{ALGOLIA_APP_ID}-dsn.algolia.net/1/indexes/{ALGOLIA_INDEX}/query"

    headers = {
        "X-Algolia-Application-Id": ALGOLIA_APP_ID,
        "X-Algolia-API-Key": ALGOLIA_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "query": "",
        "hitsPerPage": hits_per_page,
        "filters": filters
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json().get("hits", [])
    except Exception as e:
        print(f"Error querying Algolia: {e}")
        return []


def is_valid_location(job: Dict) -> bool:
    """Check if job location matches our filters (USA or Remote)."""
    # Collect all location data from various fields
    locations = []

    # Primary location fields in Algolia response
    locations.extend(job.get("tags_country", []) or [])
    locations.extend(job.get("tags_location_type", []) or [])
    locations.extend(job.get("tags_location_80k", []) or [])
    locations.extend(job.get("card_locations", []) or [])

    location_str = " ".join(str(loc) for loc in locations).lower()

    # Check for remote/global
    if any(term in location_str for term in ["remote", "global", "anywhere", "worldwide"]):
        return True

    # Check for USA locations
    if any(term in location_str for term in ["usa", "united states", "u.s.", "san francisco",
                                              "new york", "boston", "seattle", "los angeles",
                                              "california", "washington", "massachusetts",
                                              "bay area", "dc"]):
        return True

    return False


def is_excluded_area(job: Dict) -> bool:
    """Check if job is in an excluded problem area."""
    # Algolia uses tags_area for problem areas
    areas = job.get("tags_area", []) or []
    areas_card = job.get("tags_area_card", []) or []

    all_areas = [str(a).lower() for a in areas + areas_card]

    for excluded in EXCLUDED_AREAS:
        if any(excluded.lower() in area for area in all_areas):
            return True

    return False


def parse_job(hit: Dict) -> Dict:
    """Parse Algolia hit into our job format."""
    # Get locations for display
    locations = hit.get("card_locations", []) or hit.get("tags_location_80k", [])
    location_str = ", ".join(locations) if locations else "Unknown"

    return {
        "title": hit.get("title", "Unknown"),
        "company": hit.get("company_name") or "Unknown",
        "company_url": hit.get("company_url"),
        "url": hit.get("url_external") or f"https://jobs.80000hours.org/jobs/{hit.get('objectID', '')}",
        "location": location_str,
        "posted_at": hit.get("posted_at"),
        "closes_at": hit.get("closes_at"),
        "problem_areas": hit.get("tags_area", []),
        "experience_required": hit.get("tags_exp_required", []),
        "salary": hit.get("salary"),
        "source": "80000hours.org",
        "scraped_at": datetime.now().isoformat(),
        "algolia_id": hit.get("objectID")
    }


def scrape_jobs(since_date: Optional[datetime] = None, include_all_dates: bool = False) -> List[Dict]:
    """
    Scrape jobs from 80000hours.org via Algolia API.

    Args:
        since_date: Only include jobs posted after this date. If None, uses last scrape date.
        include_all_dates: If True, ignore date filtering and get all jobs.
    """
    print("Fetching jobs from 80000hours.org...")

    # Get all jobs (Algolia will return up to 1000)
    hits = search_algolia()
    print(f"  Found {len(hits)} total jobs in database")

    if not hits:
        return []

    # Determine date filter
    if include_all_dates:
        cutoff_date = None
        print("  Date filter: None (getting all jobs)")
    else:
        cutoff_date = since_date or get_last_scrape_date()
        if cutoff_date:
            print(f"  Date filter: Jobs posted after {cutoff_date.strftime('%Y-%m-%d')}")
        else:
            # First run - get jobs from last 7 days
            cutoff_date = datetime.now() - timedelta(days=7)
            print(f"  Date filter: Last 7 days (first run)")

    jobs = []
    filtered_out = {"location": 0, "area": 0, "date": 0}

    for hit in hits:
        # Location filter
        if not is_valid_location(hit):
            filtered_out["location"] += 1
            continue

        # Area filter
        if is_excluded_area(hit):
            filtered_out["area"] += 1
            continue

        # Date filter
        if cutoff_date:
            posted_at = hit.get("postedAt") or hit.get("posted_at") or hit.get("createdAt")
            if posted_at:
                try:
                    # Handle various date formats
                    if isinstance(posted_at, (int, float)):
                        post_date = datetime.fromtimestamp(posted_at / 1000 if posted_at > 1e10 else posted_at)
                    else:
                        post_date = datetime.fromisoformat(posted_at.replace("Z", "+00:00").replace("+00:00", ""))

                    if post_date < cutoff_date:
                        filtered_out["date"] += 1
                        continue
                except (ValueError, TypeError):
                    pass  # If we can't parse the date, include the job

        jobs.append(parse_job(hit))

    print(f"  Filtered out: {filtered_out['location']} (location), {filtered_out['area']} (area), {filtered_out['date']} (date)")
    print(f"  Jobs matching filters: {len(jobs)}")

    return jobs


def save_jobs(jobs: List[Dict], tag: Optional[str] = None) -> str:
    """Save jobs to a JSON file."""
    ensure_dirs()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"jobs_{timestamp}{f'_{tag}' if tag else ''}.json"
    filepath = RAW_DIR / filename

    # Deduplicate by URL
    seen_urls = set()
    unique_jobs = []
    for job in jobs:
        if job['url'] not in seen_urls:
            seen_urls.add(job['url'])
            unique_jobs.append(job)

    filepath.write_text(json.dumps({
        "scraped_at": datetime.now().isoformat(),
        "source": "80000hours.org",
        "count": len(unique_jobs),
        "filters": {
            "excluded_areas": EXCLUDED_AREAS,
            "locations": "USA, Remote, Global",
        },
        "jobs": unique_jobs
    }, indent=2))

    return str(filepath)


def run_scraper(include_all_dates: bool = False, tag: Optional[str] = None) -> dict:
    """
    Run the job scraper.

    Args:
        include_all_dates: If True, get all jobs regardless of date.
                          If False (default), only get jobs since last scrape.
        tag: Optional tag for the output filename (e.g., "test", "full")
    """
    ensure_dirs()

    print("=" * 50)
    print("80000hours.org Job Scraper")
    print("=" * 50)
    print()
    print("Filters:")
    print("  - Locations: USA, Remote, Global")
    print(f"  - Excluded areas: {', '.join(EXCLUDED_AREAS)}")
    print()

    jobs = scrape_jobs(include_all_dates=include_all_dates)

    filepath = None
    if jobs:
        filepath = save_jobs(jobs, tag=tag)
        save_last_scrape_date()
        print(f"\nSaved {len(jobs)} jobs to {filepath}")
    else:
        print("\nNo new jobs found matching filters")

    return {
        "jobs_found": len(jobs),
        "file": filepath
    }
