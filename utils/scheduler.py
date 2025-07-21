from apscheduler.schedulers.background import BackgroundScheduler
from utils.supabase_client import get_pending_weekly_emails
from utils.emailer import send_tender_email

def weekly_email_job():
    jobs = get_pending_weekly_emails()
    for job in jobs:
        send_tender_email(job["email"], job["tenders"])

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(weekly_email_job, "cron", day_of_week="thu", hour=9)  # Every Thursday at 9am
    scheduler.start()

# Optionally start scheduler at module load
start_scheduler()
