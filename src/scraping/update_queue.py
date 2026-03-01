#!/usr/bin/env python3
"""
Scrape job sources and write new postings to a temporary file for Gertrudix to analyze.

Reads per-source last-scrape dates from scrape_state.json and only includes jobs
posted after that date. New sources must be pre-populated in scrape_state.json
before running this script (the Run Scrapers skill handles that step).

Outputs:
  data/scraped_jobs/scraped_tmp.json    — new jobs from this scrape, for Gertrudix to analyze
                                           (Gertrudix writes to analyzed_jobs.json in Phase 2)
  data/scraped_jobs/latest_scrape.json  — full results of this scrape, used by the skill
                                           for stale detection against analyzed_jobs.json
  data/scraped_jobs/scrape_state.json   — updated last-scrape date per source

Usage:
    python src/scraping/update_queue.py                            # all sources
    python src/scraping/update_queue.py --sources "Anthropic"      # one source
    python src/scraping/update_queue.py --sources "Anthropic,Mistral"  # multiple
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from run_scrapers import SCRAPER_MAP

SOURCES_FILE = Path("src/scraping/sources.json")
STATE_FILE = Path("data/scraped_jobs/scrape_state.json")
TMP_FILE = Path("data/scraped_jobs/scraped_tmp.json")
LATEST_FILE = Path("data/scraped_jobs/latest_scrape.json")


def load_json(path: Path, default):
    return json.loads(path.read_text()) if path.exists() else default


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def parse_dt(s: str) -> datetime:
    dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def main():
    parser = argparse.ArgumentParser(description="Scrape sources and write new jobs to scraped_tmp.json")
    parser.add_argument(
        "--sources", type=str, default=None,
        help="Comma-separated source names to scrape (default: all)"
    )
    args = parser.parse_args()
    requested = {s.strip() for s in args.sources.split(",")} if args.sources else None

    sources_config = load_json(SOURCES_FILE, [])
    state = load_json(STATE_FILE, {})

    sources_to_run = [
        s for s in sources_config
        if requested is None or s["name"] in requested
    ]
    if not sources_to_run:
        print("No matching sources found. Check source names in src/scraping/sources.json.")
        return

    now = datetime.now(timezone.utc)
    new_jobs = []
    full_scrape = []  # all fetched jobs across sources (for latest_scrape.json)

    for source in sources_to_run:
        name = source["name"]
        source_type = source["type"]
        slug = source["slug"]
        filters = source.get("filters", {})

        last_scrape_str = state.get(name)
        if last_scrape_str is None:
            # Should not happen — skill pre-populates scrape_state.json before running
            print(f"  WARNING: No scrape date found for '{name}'. Run via the skill to set one first.")
            continue

        last_scrape_dt = parse_dt(last_scrape_str)

        scraper_class = SCRAPER_MAP.get(source_type)
        if not scraper_class:
            print(f"  Unknown type '{source_type}' for {name} — skipping")
            continue

        print(f"Fetching {name} ({source_type})...")
        scraper = scraper_class(name=name, slug=slug, filters=filters)
        jobs = scraper.run()
        print(f"  → {len(jobs)} jobs fetched")

        full_scrape.extend(j.to_dict() for j in jobs)

        # Filter to jobs posted after the last scrape date.
        # TODO: Jobs with no posted_at are included on every scrape since we can't
        # date-filter them. In practice Greenhouse/Lever/Ashby/80k all provide dates
        # reliably, so this is rare — revisit if it becomes an issue.
        before = len(jobs)
        filtered = []
        for j in jobs:
            if not j.posted_at:
                filtered.append(j)  # no date — include, can't filter
                continue
            try:
                if parse_dt(j.posted_at) > last_scrape_dt:
                    filtered.append(j)
            except Exception:
                filtered.append(j)  # unparseable date — include to be safe

        jobs = filtered
        print(f"  → {len(jobs)} posted since last scrape (filtered from {before})")

        new_jobs.extend(jobs)

        # Update this source's last-scrape date
        state[name] = now.isoformat()

    new_dicts = [j.to_dict() for j in new_jobs]

    save_json(TMP_FILE, new_dicts)
    save_json(LATEST_FILE, full_scrape)
    save_json(STATE_FILE, state)

    print(f"\n{'=' * 45}")
    print(f"New jobs to analyze     : {len(new_dicts)}")
    print(f"Saved to                : {TMP_FILE}")
    print(f"Full scrape saved to    : {LATEST_FILE}")


if __name__ == "__main__":
    main()
