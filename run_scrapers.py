#!/usr/bin/env python3
"""
Run job scrapers to fetch new opportunities.

Usage:
    python run_scrapers.py              # Get jobs since last scrape (default)
    python run_scrapers.py --all        # Get all jobs (ignore date filter)
    python run_scrapers.py --tag test   # Add tag to output filename
"""

import argparse
from src.scrapers.job_scraper import run_scraper

def main():
    parser = argparse.ArgumentParser(description="Scrape job listings from 80000hours.org")
    parser.add_argument("--all", action="store_true",
                       help="Get all jobs (ignore date filter)")
    parser.add_argument("--tag", type=str, default=None,
                       help="Tag for output filename (e.g., 'test', 'full')")
    args = parser.parse_args()

    result = run_scraper(
        include_all_dates=args.all,
        tag=args.tag
    )

    print()
    print(f"Total jobs found: {result['jobs_found']}")
    if result.get('file'):
        print(f"Saved to: {result['file']}")


if __name__ == "__main__":
    main()
