from fastapi import FastAPI, BackgroundTasks, Request
from orchestration.run_pipeline import run_pipeline_with_params
from utils.supabase_client import save_tender_data
from utils.emailer import send_tender_email

app = FastAPI()

@app.post("/fillout-webhook")
async def fillout_webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    print("Webhook data:", data)

    # Parse Fillout webhook fields
    answers = {a['field']['id']: (a.get('email') or a.get('text')) for a in data['answers']}
    first_name = answers.get('name', '')
    user_email = answers.get('email', '')
    keyword = answers.get('keyword', '')
    cpv = answers.get('cpv', '')

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
