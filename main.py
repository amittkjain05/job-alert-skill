# main.py
from dotenv import load_dotenv
from job_fetcher import fetch_indeed_jobs, fetch_remotive_jobs
from claude_filter import filter_and_rank_jobs
from email_sender import send_job_report

load_dotenv()

MY_SKILLS = ["Python", "FastAPI", "AWS", "PostgreSQL", "Docker"]
MY_EMAIL  = "you@gmail.com"

def run_job_alert():
    print("⏳ Fetching jobs...")
    all_jobs = []
    all_jobs += fetch_indeed_jobs(MY_SKILLS)
    all_jobs += fetch_remotive_jobs(MY_SKILLS)
    
    if not all_jobs:
        print("No new jobs found in last 12 hours.")
        return
    
    print(f"📋 Found {len(all_jobs)} raw jobs. Filtering with Claude...")
    filtered = filter_and_rank_jobs(all_jobs, MY_SKILLS)
    
    print(f"✅ {len(filtered)} relevant jobs. Sending email...")
    send_job_report(filtered, MY_EMAIL, MY_SKILLS)

if __name__ == "__main__":
    run_job_alert()
