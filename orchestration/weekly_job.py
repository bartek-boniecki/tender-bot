import logging
import asyncio
from dotenv import load_dotenv

load_dotenv(override=False)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tender-bot.weekly")

from utils.supabase_client import (
    get_all_users,
    get_user_preferences,
    save_tender_data,
)
from orchestration.run_pipeline import run_pipeline_with_params
from utils.emailer import send_tender_email

def weekly_job():
    users = get_all_users()
    if not users:
        logger.info("No users to process")
        return

    for u in users:
        user_id = u.get("id")
        first_name = u.get("first_name")
        email = u.get("email")

        cpv, keyword = get_user_preferences(user_id)
        if not all([cpv, keyword]):
            logger.warning(f"No saved preferences for {email}, skipping.")
            continue

        logger.info(f"Weekly run for {email} ({cpv} + {keyword})")
        try:
            tenders = asyncio.run(run_pipeline_with_params(cpv, keyword))
        except Exception:
            logger.exception(f"Pipeline failed for {email}")
            continue

        new_tenders = save_tender_data(first_name, email, cpv, keyword, tenders)
        logger.info(f"Saved {len(new_tenders)} new tenders for {email}")

        if new_tenders:
            try:
                send_tender_email(email, new_tenders, keyword, cpv, first_name)
            except Exception:
                logger.exception(f"Failed sending email to {email}")

if __name__ == "__main__":
    weekly_job()
