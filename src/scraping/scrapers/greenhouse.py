import requests
from datetime import datetime
from .base import BaseScraper, Job


class GreenhouseScraper(BaseScraper):
    source_type = "greenhouse"

    def fetch_jobs(self) -> list[Job]:
        url = f"https://boards-api.greenhouse.io/v1/boards/{self.slug}/jobs?content=true"
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"  Error fetching {self.name} (Greenhouse): {e}")
            return []

        jobs = []
        for item in data.get("jobs", []):
            location = item.get("location", {}).get("name", "Unknown")
            departments = item.get("departments", [])
            dept = departments[0]["name"] if departments else ""

            jobs.append(Job(
                title=item.get("title", "Unknown"),
                company=self.name,
                url=item.get("absolute_url", ""),
                location=location,
                department=dept,
                posted_at=item.get("updated_at"),
                source_type=self.source_type,
                scraped_at=datetime.now().isoformat(),
            ))

        return jobs
