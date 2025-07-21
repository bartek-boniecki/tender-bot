from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from orchestration.run_pipeline import run_pipeline_with_params
from utils.supabase_client import save_tender_data
from utils.emailer import send_tender_email
import asyncio

app = FastAPI()

class Answer(BaseModel):
    email: str = None
    text: str = None

class FormResponse(BaseModel):
    answers: list[Answer]

class WebhookRequest(BaseModel):
    form_response: FormResponse

def process_pipeline(first_name, user_email, cpv, keyword):
    try:
        tenders = asyncio.run(run_pipeline_with_params(cpv, keyword))
        tenders = tenders[:20]
        print(f"Tenders found (limited to 20): {tenders}")

        save_tender_data(first_name, user_email, cpv, keyword, tenders)
        send_tender_email(user_email, tenders)
    except Exception as e:
        print(f"Error in pipeline: {e}")

@app.post("/typeform-webhook")
async def typeform_webhook(data: WebhookRequest, background_tasks: BackgroundTasks):
    print("Webhook received:", data)
    answers = data.form_response.answers
    first_name = answers[0].text or ""
    user_email = answers[1].email or ""
    keyword = answers[3].text or ""
    cpv = answers[2].text or ""
    print("Parsed values:", first_name, user_email, cpv, keyword)

    background_tasks.add_task(process_pipeline, first_name, user_email, cpv, keyword)
    return {"status": "accepted"}
