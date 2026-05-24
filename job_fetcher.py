# job_fetcher.py
import feedparser
import requests
from datetime import datetime, timedelta

def fetch_indeed_jobs(skills: list[str], location: str = "India") -> list[dict]:
    query = "+".join(skills)
    url = f"https://in.indeed.com/rss?q={query}&l={location}&fromage=1&sort=date"
    feed = feedparser.parse(url)
    
    jobs = []
    cutoff = datetime.now() - timedelta(hours=12)
    
    for entry in feed.entries:
        published = datetime(*entry.published_parsed[:6])
        if published >= cutoff:
            jobs.append({
                "title": entry.title,
                "company": entry.get("source", {}).get("title", "Unknown"),
                "link": entry.link,
                "description": entry.summary,
                "posted_at": published.strftime("%Y-%m-%d %H:%M"),
                "source": "Indeed"
            })
    return jobs

def fetch_remotive_jobs(skills: list[str]) -> list[dict]:
    # Free API — no key needed
    url = "https://remotive.com/api/remote-jobs"
    resp = requests.get(url, params={"search": " ".join(skills), "limit": 20})
    jobs = []
    cutoff = datetime.now() - timedelta(hours=12)
    
    for job in resp.json().get("jobs", []):
        posted = datetime.fromisoformat(job["publication_date"].replace("Z", ""))
        if posted >= cutoff:
            jobs.append({
                "title": job["title"],
                "company": job["company_name"],
                "link": job["url"],
                "description": job["description"][:300],
                "posted_at": posted.strftime("%Y-%m-%d %H:%M"),
                "source": "Remotive"
            })
    return jobs
