# linkedin_fetcher.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import re

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

def parse_linkedin_time(time_text: str) -> datetime | None:
    """
    Converts LinkedIn relative time strings like '3 hours ago',
    '45 minutes ago' into a datetime object.
    """
    now = datetime.now()
    time_text = time_text.lower().strip()

    match = re.search(r"(\d+)\s+(second|minute|hour|day)", time_text)
    if not match:
        return None

    value, unit = int(match.group(1)), match.group(2)
    deltas = {
        "second": timedelta(seconds=value),
        "minute": timedelta(minutes=value),
        "hour":   timedelta(hours=value),
        "day":    timedelta(days=value),
    }
    return now - deltas.get(unit, timedelta(days=99))


def fetch_linkedin_jobs(
    skills: list[str],
    location: str = "India",
    max_pages: int = 3
) -> list[dict]:
    """
    Scrapes LinkedIn public job listings posted in the last 12 hours.

    Args:
        skills:    List of skill keywords e.g. ["Python", "FastAPI", "AWS"]
        location:  Job location string e.g. "India", "Bangalore"
        max_pages: Number of result pages to scrape (25 results per page)

    Returns:
        List of job dicts with title, company, location, link, posted_at, source
    """
    query    = "%20".join(skills)
    cutoff   = datetime.now() - timedelta(hours=12)
    jobs     = []

    for page in range(max_pages):
        start = page * 25  # LinkedIn paginates in steps of 25

        # f_TPR=r43200 filters for jobs posted in last 12 hours (43200 seconds)
        # sortBy=DD    sorts by most recent first
        url = (
            f"https://www.linkedin.com/jobs/search/"
            f"?keywords={query}"
            f"&location={location}"
            f"&f_TPR=r43200"
            f"&sortBy=DD"
            f"&start={start}"
        )

        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[LinkedIn] Page {page+1} fetch error: {e}")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.find_all("div", class_=re.compile(r"base-card"))

        if not cards:
            print(f"[LinkedIn] No more cards found at page {page+1}. Stopping.")
            break

        for card in cards:
            try:
                # --- Title ---
                title_tag = card.find("h3", class_=re.compile(r"base-search-card__title"))
                title = title_tag.get_text(strip=True) if title_tag else "N/A"

                # --- Company ---
                company_tag = card.find("h4", class_=re.compile(r"base-search-card__subtitle"))
                company = company_tag.get_text(strip=True) if company_tag else "N/A"

                # --- Location ---
                location_tag = card.find("span", class_=re.compile(r"job-search-card__location"))
                job_location = location_tag.get_text(strip=True) if location_tag else "N/A"

                # --- Link ---
                link_tag = card.find("a", class_=re.compile(r"base-card__full-link"))
                link = link_tag["href"].split("?")[0] if link_tag else "#"

                # --- Posted Time ---
                time_tag = card.find("time")
                if time_tag:
                    # Prefer datetime attribute for accuracy
                    dt_attr = time_tag.get("datetime")
                    if dt_attr:
                        posted_at = datetime.fromisoformat(dt_attr[:19])
                    else:
                        posted_at = parse_linkedin_time(time_tag.get_text(strip=True))
                else:
                    posted_at = None

                # --- 12-hour filter ---
                if posted_at and posted_at < cutoff:
                    continue  # Too old, skip

                jobs.append({
                    "title":      title,
                    "company":    company,
                    "location":   job_location,
                    "link":       link,
                    "posted_at":  posted_at.strftime("%Y-%m-%d %H:%M") if posted_at else "Unknown",
                    "description": f"{title} at {company} in {job_location}",
                    "source":     "LinkedIn",
                })

            except Exception as e:
                print(f"[LinkedIn] Error parsing card: {e}")
                continue

        print(f"[LinkedIn] Page {page+1} scraped — {len(jobs)} jobs so far")
        time.sleep(2)  # Polite delay between pages to avoid rate limiting

    print(f"[LinkedIn] Total jobs found in last 12h: {len(jobs)}")
    return jobs
