from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


@dataclass
class Job:
    title: str
    company: str
    url: str
    location: str
    department: str
    posted_at: Optional[str]
    source_type: str
    scraped_at: str

    def to_dict(self):
        return asdict(self)


class BaseScraper:
    source_type = "base"

    def __init__(self, name: str, slug: str, filters: dict):
        self.name = name
        self.slug = slug
        self.filters = filters

    def fetch_jobs(self) -> list[Job]:
        raise NotImplementedError

    def apply_filters(self, jobs: list[Job]) -> list[Job]:
        location_filter = [l.lower() for l in self.filters.get("locations", [])]
        dept_filter = [d.lower() for d in self.filters.get("departments", [])]

        filtered = []
        for job in jobs:
            # Location filter: pass if no filter set, or if job location matches, or if remote
            if location_filter:
                job_loc = job.location.lower()
                if not any(loc in job_loc for loc in location_filter) and "remote" not in job_loc:
                    continue

            # Department filter: pass if no filter set, or if job dept matches
            if dept_filter:
                job_dept = job.department.lower()
                if not any(dept in job_dept for dept in dept_filter):
                    continue

            filtered.append(job)

        return filtered

    def run(self) -> list[Job]:
        jobs = self.fetch_jobs()
        return self.apply_filters(jobs)
