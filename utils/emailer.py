import os
from supabase import create_client
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import re

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

def summary_to_html(summary):
    # Replace markdown-style **bold** with real <b>
    html = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', summary)
    # Replace lines starting with - (dash+space) to <li>
    html = re.sub(r'^\s*-\s+', r'<li>', html, flags=re.MULTILINE)
    # Wrap bullet points in <ul>
    if '<li>' in html:
        html = re.sub(r'(<li>.*?)(?=\n[^-]|$)', r'<ul>\1</ul>', html, flags=re.DOTALL)
    # Replace line breaks with <br> for spacing
    html = html.replace('\n', '<br>')
    return html

def build_tenders_html(tenders):
    html = ""
    for tender in tenders:
        summary = tender.get('summary', '')
        html += summary_to_html(summary)
        # Add a link at the end (always clickable)
        if tender.get('url'):
            html += f'<br><a href="{tender["url"]}" style="color:#1a3767;text-decoration:underline;">Tender link</a><br><br>'
    # Wrap everything in a styled <div>
    return (
        "<div style='font-family:Segoe UI,Arial,sans-serif;font-size:16px;line-height:1.7;color:#212121;'>"
        f"{html}"
        "</div>"
    )

def send_tender_email(user_email, tenders):
    # Use Brevo API to send email
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = os.getenv("BREVO_API_KEY")  # Set this in Railway!

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    first_name = get_user_first_name(user_email)
    tenders_html = build_tenders_html(tenders)

    # Replace TEMPLATE_ID with your real template ID from Brevo
    template_id = 1  # <--- CHANGE THIS to your actual Brevo template ID

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": user_email, "name": first_name or "User"}],
        template_id=template_id,
        params={
            "first_name": first_name,
            "tenders_html": tenders_html
        }
    )

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print("Brevo API response:", api_response)
    except ApiException as e:
        print("Exception when calling Brevo API: %s\n" % e)
