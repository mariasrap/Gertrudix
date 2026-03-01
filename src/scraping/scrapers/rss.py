import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from .base import BaseScraper, Job


class RSSScraper(BaseScraper):
    """Generic RSS/Atom feed scraper. Set slug to the full feed URL."""
    source_type = "rss"

    def fetch_jobs(self) -> list[Job]:
        url = self.slug  # For RSS, slug is the full feed URL
        try:
            response = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            root = ET.fromstring(response.content)
        except Exception as e:
            print(f"  Error fetching {self.name} (RSS): {e}")
            return []

        # Support both RSS 2.0 (<channel><item>) and Atom (<feed><entry>)
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        items = root.findall(".//item")  # RSS 2.0
        if not items:
            items = root.findall(".//atom:entry", ns)  # Atom

        jobs = []
        for item in items:
            title = self._text(item, ["title", "atom:title"], ns) or "Unknown"
            link = self._text(item, ["link", "atom:link"], ns) or ""
            # Atom <link> is an attribute, not text
            if not link:
                link_el = item.find("atom:link", ns)
                if link_el is not None:
                    link = link_el.get("href", "")

            pub_date = self._text(item, ["pubDate", "atom:published", "atom:updated"], ns)
            posted_at = None
            if pub_date:
                try:
                    posted_at = parsedate_to_datetime(pub_date).isoformat()
                except Exception:
                    try:
                        # ISO 8601 (Atom)
                        posted_at = datetime.fromisoformat(pub_date.replace("Z", "+00:00")).isoformat()
                    except Exception:
                        pass

            # RSS feeds rarely include structured location/dept — leave as Unknown/empty
            jobs.append(Job(
                title=title,
                company=self.name,
                url=link,
                location="Unknown",
                department="",
                posted_at=posted_at,
                source_type=self.source_type,
                scraped_at=datetime.now().isoformat(),
            ))

        return jobs

    @staticmethod
    def _text(element, tags: list, ns: dict) -> str:
        for tag in tags:
            el = element.find(tag, ns)
            if el is not None and el.text:
                return el.text.strip()
        return ""
