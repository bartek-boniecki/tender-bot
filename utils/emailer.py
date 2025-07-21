import os
import smtplib
from email.mime.text import MIMEText
from supabase import create_client

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USERNAME)

def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

def get_user_first_name(email):
    supabase = get_supabase_client()
    try:
        res = supabase.table("users").select("first_name").eq("email", email).execute()
        if res.data and len(res.data) > 0:
            return res.data[0].get("first_name", "")
        else:
            return ""
    except Exception as e:
        print(f"Error fetching first name: {e}")
        return ""

def send_tender_email(user_email, tenders):
    first_name = get_user_first_name(user_email)
    if first_name:
        greeting = f"Hi {first_name},"
    else:
        greeting = "Hello,"
    subject = "Your Tender Participation Requirements Digest"
    body = f"{greeting}\n\nHere are your latest tenders:\n\n"
    for tender in tenders:
        body += f"{tender['url']}\n{tender['summary']}\n\n"
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = user_email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, [user_email], msg.as_string())
        print(f"Sent email to {user_email}")
    except Exception as e:
        print(f"Error sending email to {user_email}: {e}")