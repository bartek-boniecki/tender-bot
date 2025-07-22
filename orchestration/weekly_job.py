from utils.supabase_client import get_all_users, save_tender_data
from orchestration.run_pipeline import run_pipeline_with_params
from utils.emailer import send_tender_email
from asyncio import run as arun

def weekly_job():
    users = get_all_users()
    for user in users:
        first_name = user['first_name']
        user_email = user['email']
        keyword = user['keyword']
        cpv = user['cpv']
        tenders = arun(run_pipeline_with_params(cpv, keyword))
        tenders = tenders[:20]
        save_tender_data(first_name, user_email, cpv, keyword, tenders)
        send_tender_email(user_email, tenders, keyword, cpv, first_name)

if __name__ == "__main__":
    weekly_job()
