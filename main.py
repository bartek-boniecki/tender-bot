import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Request, BackgroundTasks

# Only load a local .env if no real env vars exist
load_dotenv(override=False)

from orchestration.run_pipeline import run_pipeline_with_params
from utils.supabase_client import save_tender_data
from utils.emailer import send_tender_email

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tender-bot")

app = FastAPI()

@app.post("/fillout-webhook")
async def fillout_webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    logger.info("Received webhook payload")
    
    questions = data.get("submission", {}).get("questions", [])
    answers = {q["name"]: q["value"] for q in questions}

    first_name = answers.get("What's your name", "").strip()
    user_email = answers.get("What is your email?", "").strip()
    keyword    = answers.get("Provide one keyword we'll use to look up tenders for you", "").strip()
    raw_cpv    = answers.get("Provide one CPV code to narrow down our search", "").strip()
    cpv        = raw_cpv.split()[0] if raw_cpv else ""

    if not all([first_name, user_email, keyword, cpv]):
        logger.error("Missing required fields")
        return {"status": "error", "reason": "Missing required fields"}

    try:
        logger.info(f"Starting pipeline for {user_email}")
        tenders = await run_pipeline_with_params(cpv, keyword)
    except Exception:
        logger.exception("Pipeline execution failed")
        return {"status": "error", "reason": "Pipeline execution failed"}

    new_tenders = save_tender_data(first_name, user_email, cpv, keyword, tenders)
    logger.info(f"Persisted {len(new_tenders)} new tenders")

    if new_tenders:
        background_tasks.add_task(
            send_tender_email,
            user_email, new_tenders, keyword, cpv, first_name
        )
    else:
        logger.info("No new tenders to email")

    return {"status": "success", "new_tenders": len(new_tenders)}
