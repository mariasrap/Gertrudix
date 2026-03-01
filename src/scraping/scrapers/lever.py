import requests
from datetime import datetime
from .base import BaseScraper, Job


class LeverScraper(BaseScraper):
    source_type = "lever"

    def fetch_jobs(self) -> list[Job]:
        url = f"https://api.lever.co/v0/postings/{self.slug}?mode=json"
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"  Error fetching {self.name} (Lever): {e}")
            return []

        jobs = []
        for item in data:
            categories = item.get("categories", {})

            # Location: try categories.location, then allLocations list
            location = categories.get("location", "")
            if not location:
                all_locs = categories.get("allLocations", [])
                location = all_locs[0] if all_locs else "Unknown"

            dept = categories.get("department", "") or categories.get("team", "")

            # Lever createdAt is a Unix timestamp in ms
            posted_at = None
            ts = item.get("createdAt")
            if ts:
                try:
                    posted_at = datetime.fromtimestamp(ts / 1000).isoformat()
                except (ValueError, TypeError):
                    pass

            jobs.append(Job(
                title=item.get("text", "Unknown"),
                company=self.name,
                url=item.get("hostedUrl", ""),
                location=location,
                department=dept,
                posted_at=posted_at,
                source_type=self.source_type,
                scraped_at=datetime.now().isoformat(),
            ))

        return jobs
