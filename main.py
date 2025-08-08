import os
from dotenv import load_dotenv
import logging
from fastapi import FastAPI, Request, BackgroundTasks

# Only load local .env if it doesn't overwrite Railway’s env vars
load_dotenv(override=False)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tender-bot")

from orchestration.run_pipeline import run_pipeline_with_params
from utils.supabase_client import save_tender_data
from utils.emailer import send_tender_email

app = FastAPI()

@app.post("/fillout-webhook")
async def fillout_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    1) Parse form data
    2) Scrape & summarize against TED
    3) Persist in Supabase
    4) ALWAYS send the user an email with the results
    """
    data = await request.json()
    logger.info("Received webhook payload")

    # Extract answers by question‐name
    questions = data.get("submission", {}).get("questions", [])
    answers = {q["name"]: q["value"] for q in questions}

    first_name = answers.get("What's your name", "").strip()
    user_email = answers.get("What is your email?", "").strip()
    keyword    = answers.get("Provide one keyword we'll use to look up tenders for you", "").strip()
    raw_cpv    = answers.get("Provide one CPV code to narrow down our search", "").strip()
    cpv        = raw_cpv.split()[0] if raw_cpv else ""

    if not all([first_name, user_email, keyword, cpv]):
        logger.error("Missing required fields in webhook payload")
        return {"status": "error", "reason": "Missing required fields"}

    # 2) Run the pipeline
    try:
        logger.info(f"Starting pipeline for {user_email} ({cpv} + {keyword})")
        tenders = await run_pipeline_with_params(cpv, keyword)
    except Exception:
        logger.exception("Pipeline execution failed")
        return {"status": "error", "reason": "Pipeline execution failed"}

    # 3) Persist only brand‑new tenders
    new_tenders = save_tender_data(first_name, user_email, cpv, keyword, tenders)
    logger.info(f"Persisted {len(new_tenders)} new tenders for {user_email}")

    # 4) ALWAYS send an email: use new_tenders if any, else send the full scraped list
    tenders_to_email = new_tenders or tenders
    background_tasks.add_task(
        send_tender_email,
        user_email,
        tenders_to_email,
        keyword,
        cpv,
        first_name
    )
    logger.info(f"Scheduled email to {user_email} with {len(tenders_to_email)} tenders")

    return {"status": "success", "new_tenders": len(new_tenders)}
