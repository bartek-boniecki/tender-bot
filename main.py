import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, BackgroundTasks

load_dotenv(override=True)

from orchestration.run_pipeline import run_pipeline_with_params
from utils.supabase_client import save_tender_data
from utils.emailer import send_tender_email

app = FastAPI()

@app.post("/fillout-webhook")
async def fillout_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Triggered by a Fillout form submission webhook.
    1) Parse name, email, keyword, CPV
    2) Run scrape→summarize pipeline
    3) Persist only new tenders in Supabase
    4) Send results by email (background task)
    """
    data = await request.json()
    questions = data.get("submission", {}).get("questions", [])
    answers = {q["name"]: q["value"] for q in questions}

    # Extract & normalize fields
    first_name = answers.get("What's your name", "").strip()
    user_email = answers.get("What is your email?", "").strip()
    keyword    = answers.get("Provide one keyword we'll use to look up tenders for you", "").strip()
    raw_cpv    = answers.get("Provide one CPV code to narrow down our search", "").strip()
    cpv        = raw_cpv.split()[0] if raw_cpv else ""

    # Validate
    if not all([first_name, user_email, keyword, cpv]):
        return {"status": "error", "reason": "Missing required fields"}

    try:
        # 1) Scrape & summarize
        tenders = run_pipeline_with_params(cpv, keyword)

        # 2) Persist & filter to only brand‑new results
        new_tenders = save_tender_data(first_name, user_email, cpv, keyword, tenders)

        # 3) Send email in the background so we don’t block the webhook
        background_tasks.add_task(
            send_tender_email,
            user_email, new_tenders, keyword, cpv, first_name
        )

        return {"status": "success", "new_tenders": len(new_tenders)}

    except Exception as e:
        print(f"[main.py] pipeline error: {e}")
        return {"status": "error", "reason": str(e)}
