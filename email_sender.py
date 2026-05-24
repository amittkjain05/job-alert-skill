# email_sender.py
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

def send_job_report(jobs: list[dict], recipient: str, skillset: list[str]):
    html = f"""
    <html><body>
    <h2>🔍 Job Alert — Last 12 Hours</h2>
    <p><strong>Skills:</strong> {', '.join(skillset)}</p>
    <p><strong>Found:</strong> {len(jobs)} matching jobs</p>
    <hr/>
    """
    
    for job in sorted(jobs, key=lambda x: x.get("rank", 99)):
        html += f"""
        <div style="border:1px solid #ddd; padding:12px; margin:10px 0; border-radius:6px;">
            <h3>#{job.get('rank')} {job['title']} — {job['company']}</h3>
            <p>📅 Posted: {job['posted_at']} | 🌐 Source: {job['source']}</p>
            <p>✅ <em>{job.get('match_reason', '')}</em></p>
            <a href="{job['link']}">👉 Apply Now</a>
        </div>
        """
    
    html += "</body></html>"
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🚀 {len(jobs)} New Jobs Found | {', '.join(skillset[:3])}"
    msg["From"] = os.getenv("GMAIL_USER")
    msg["To"] = recipient
    msg.attach(MIMEText(html, "html"))
    
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(os.getenv("GMAIL_USER"), os.getenv("GMAIL_APP_PASSWORD"))
        server.sendmail(msg["From"], recipient, msg.as_string())
    
    print(f"✅ Email sent with {len(jobs)} jobs!")
