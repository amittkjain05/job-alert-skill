# main.py
from dotenv import load_dotenv
from job_fetcher import fetch_indeed_jobs, fetch_remotive_jobs
from linkedin_fetcher import fetch_linkedin_jobs           # ← Approach 1
# from linkedin_selenium_fetcher import fetch_linkedin_jobs_selenium  # ← Approach 2
from claude_filter import filter_and_rank_jobs
from email_sender import send_job_report

load_dotenv()

MY_SKILLS = ["Python", "FastAPI", "AWS", "PostgreSQL", "Docker"]
MY_EMAIL  = "you@gmail.com"

def run_job_alert():
    print("⏳ Fetching jobs from all sources...")
    all_jobs = []

    all_jobs += fetch_indeed_jobs(MY_SKILLS)
    all_jobs += fetch_remotive_jobs(MY_SKILLS)
    all_jobs += fetch_linkedin_jobs(MY_SKILLS, location="India")  # ← New

    # Deduplicate by job title + company
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        key = (job["title"].lower(), job["company"].lower())
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)

    print(f"📋 {len(unique_jobs)} unique jobs after dedup. Filtering with Claude...")

    if not unique_jobs:
        print("No new jobs in last 12 hours.")
        return

    filtered = filter_and_rank_jobs(unique_jobs, MY_SKILLS)
    print(f"✅ {len(filtered)} relevant jobs. Sending email...")
    send_job_report(filtered, MY_EMAIL, MY_SKILLS)

if __name__ == "__main__":
    run_job_alert()
