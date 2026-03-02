from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from scrapers.ashby import AshbyScraper
from scrapers.base import Job
from scrapers.greenhouse import GreenhouseScraper
from scrapers.lever import LeverScraper
from scrapers.rss import RSSScraper

SCRAPER_MAP = {
    "greenhouse": GreenhouseScraper,
    "lever": LeverScraper,
    "ashby": AshbyScraper,
    "rss": RSSScraper,
}


def run_all(sources_path: Path | None = None) -> list[Job]:
    if sources_path is None:
        sources_path = Path(__file__).parent / "sources.json"

    with open(sources_path) as f:
        sources = json.load(f)

    all_jobs = []
    for source in sources:
        name = source["name"]
        source_type = source["type"]
        slug = source["slug"]
        filters = source.get("filters", {})

        scraper_class = SCRAPER_MAP.get(source_type)
        if not scraper_class:
            print(f"  Unknown source type '{source_type}' for {name} — skipping")
            continue

        print(f"Fetching {name} ({source_type})...")
        scraper = scraper_class(name=name, slug=slug, filters=filters)
        jobs = scraper.run()
        print(f"  → {len(jobs)} jobs")
        all_jobs.extend(jobs)

    return all_jobs


def main():
    print("Running job scrapers...\n")
    jobs = run_all()

    output_dir = Path("data/scraped_jobs")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"jobs_{timestamp}.json"

    with open(output_file, "w") as f:
        json.dump([j.to_dict() for j in jobs], f, indent=2)

    print(f"\nTotal: {len(jobs)} jobs saved to {output_file}")


if __name__ == "__main__":
    main()
