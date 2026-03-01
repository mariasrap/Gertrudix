import requests
from datetime import datetime
from .base import BaseScraper, Job


class AshbyScraper(BaseScraper):
    source_type = "ashby"

    def fetch_jobs(self) -> list[Job]:
        url = f"https://jobs.ashbyhq.com/api/non-user-facing/job-board/{self.slug}"
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"  Error fetching {self.name} (Ashby): {e}")
            return []

        jobs = []
        for item in data.get("jobPostings", []):
            location = item.get("locationName", "") or item.get("location", "Unknown")
            dept = item.get("departmentName", "") or item.get("teamName", "")

            jobs.append(Job(
                title=item.get("title", "Unknown"),
                company=self.name,
                url=f"https://jobs.ashbyhq.com/{self.slug}/{item.get('id', '')}",
                location=location,
                department=dept,
                posted_at=item.get("publishedDate"),
                source_type=self.source_type,
                scraped_at=datetime.now().isoformat(),
            ))

        return jobs
