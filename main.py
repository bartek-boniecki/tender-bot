import os
from dotenv import load_dotenv
load_dotenv(override=True)

from fastapi import FastAPI, BackgroundTasks, Request
from orchestration.run_pipeline import run_pipeline_with_params
from utils.supabase_client import save_tender_data
from utils.emailer import send_tender_email

app = FastAPI()

@app.post("/fillout-webhook")
async def fillout_webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    print("Webhook data:", data)
    questions = data['submission']['questions']
    answers_by_name = {q['name']: q['value'] for q in questions}
    first_name = answers_by_name.get("What's your name", "")
    user_email = answers_by_name.get("What is your email?", "")
    keyword = answers_by_name.get("Provide one keyword we'll use to look up tenders for you", "")
    raw_cpv = answers_by_name.get("Provide one CPV code to narrow down our search", "")
    cpv = raw_cpv.split()[0] if raw_cpv else ""
    if not all([first_name, user_email, keyword, cpv]):
        return {"status": "error", "reason": "Missing required fields"}
    background_tasks.add_task(process_pipeline, first_name, user_email, cpv, keyword)
    return {"status": "accepted"}

def process_pipeline(first_name, user_email, cpv, keyword):
    try:
        from asyncio import run as arun
        tenders = arun(run_pipeline_with_params(cpv, keyword))
        tenders = tenders[:20]
        save_tender_data(first_name, user_email, cpv, keyword, tenders)
        send_tender_email(user_email, tenders, keyword, cpv, first_name)
    except Exception as e:
        print(f"Pipeline error: {e}")
