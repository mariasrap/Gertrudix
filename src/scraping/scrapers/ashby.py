import requests
from datetime import datetime
from .base import BaseScraper, Job


class AshbyScraper(BaseScraper):
    source_type = "ashby"

    def fetch_jobs(self) -> list[Job]:
        url = f"https://api.ashbyhq.com/posting-api/job-board/{self.slug}"
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"  Error fetching {self.name} (Ashby): {e}")
            return []

        jobs = []
        for item in data.get("jobs", []):
            location = item.get("location", "Unknown")
            dept = item.get("department", "") or item.get("team", "")

            jobs.append(Job(
                title=item.get("title", "Unknown"),
                company=self.name,
                url=item.get("jobUrl", f"https://jobs.ashbyhq.com/{self.slug}/{item.get('id', '')}"),
                location=location,
                department=dept,
                posted_at=item.get("publishedAt"),
                source_type=self.source_type,
                scraped_at=datetime.now().isoformat(),
            ))

        return jobs
