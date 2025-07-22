import os
from dotenv import load_dotenv
import asyncio

load_dotenv(override=True)

from utils.supabase_client import get_all_users, save_tender_data
from orchestration.run_pipeline import run_pipeline_with_params
from utils.emailer import send_tender_email

def weekly_job():
    users = get_all_users()
    for u in users:
        first_name = u.get('first_name')
        email      = u.get('email')
        keyword    = u.get('keyword')
        cpv        = u.get('cpv')

        # 1) Scrape & summarize
        tenders = asyncio.run(run_pipeline_with_params(cpv, keyword))
        tenders = tenders[:20]

        # 2) Save & filter to only brand‐new ones
        new_tenders = save_tender_data(first_name, email, cpv, keyword, tenders)

        # 3) Send email if there are any new tenders
        if new_tenders:
            send_tender_email(email, new_tenders, keyword, cpv, first_name)

if __name__ == "__main__":
    weekly_job()
