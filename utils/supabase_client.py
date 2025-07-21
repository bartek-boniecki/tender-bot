import os
from supabase import create_client
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import re

# --- SUPABASE SECTION ---

def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

def get_or_create_user(first_name, email):
    supabase = get_supabase_client()
    try:
        res = supabase.table("users").select("id, first_name").eq("email", email).execute()
        if res.data and len(res.data) > 0:
            user_id = res.data[0]['id']
            if not res.data[0].get("first_name") or res.data[0].get("first_name") != first_name:
                supabase.table("users").update({"first_name": first_name}).eq("id", user_id).execute()
            return user_id
        else:
            insert_res = supabase.table("users").insert({"email": email, "first_name": first_name}).execute()
            if insert_res.data and len(insert_res.data) > 0:
                return insert_res.data[0]['id']
    except Exception as e:
        print(f"Error in get_or_create_user: {e}")
    return None

def save_tender_data(first_name, email, cpv, keyword, tenders):
    supabase = get_supabase_client()
    user_id = get_or_create_user(first_name, email)
    if not user_id:
        print("User creation failed")
        return None
    for tender in tenders:
        data = {
            "user_id": user_id,
            "cpv": cpv,
            "keyword": keyword,
            "tender_url": tender["url"],
            "criteria_summary": tender["summary"],
        }
        try:
            supabase.table("tenders").insert(data).execute()
        except Exception as e:
            print(f"Error saving tender: {e}")
    return user_id

# --- EMAILER SECTION ---

def summary_to_html(summary):
    # Use markdown for email template, convert at sending step
    summary = summary.replace('\n', '<br>')
    summary = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', summary)
    summary = re.sub(r'^\s*-\s+', r'<li>', summary, flags=re.MULTILINE)
    if '<li>' in summary:
        summary = re.sub(r'(<li>.*?)(?=\n[^-]|$)', r'<ul>\1</ul>', summary, flags=re.DOTALL)
    return summary

def build_tenders_html(tenders):
    html = ""
    for tender in tenders:
        summary = tender.get('summary', '')
        html += summary_to_html(summary)
        if tender.get('url'):
            html += f'<br><a href="{tender["url"]}" style="color:#1a3767;text-decoration:underline;">Tender link</a><br><br>'
    return (
        "<div style='font-family:Segoe UI,Arial,sans-serif;font-size:16px;line-height:1.7;color:#212121;'>"
        f"{html}"
        "</div>"
    )

def send_tender_email(user_email, first_name, cpv, keyword, tenders):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = os.getenv("BREVO_API_KEY")
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    tenders_html = build_tenders_html(tenders)
    # Insert your Brevo template_id!
    template_id = 1

    # Sentence at the top with variables
    intro = f"We heard you are looking for tenders in the <b>{keyword}</b> area under <b>{cpv}</b> category - here you are:<br><br>"

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": user_email, "name": first_name or "User"}],
        template_id=template_id,
        params={
            "first_name": first_name,
            "tenders_html": intro + tenders_html
        }
    )

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print("Brevo API response:", api_response)
    except ApiException as e:
        print("Exception when calling Brevo API: %s\n" % e)

# --- COMBINED CALL ---

def save_and_email(first_name, email, cpv, keyword, tenders):
    user_id = save_tender_data(first_name, email, cpv, keyword, tenders)
    if user_id:
        send_tender_email(email, first_name, cpv, keyword, tenders)
    else:
        print("Email not sent: User ID missing")

# --- Usage: call this function when you process your webhook/form ---
# Example
# save_and_email(first_name, email, cpv, keyword, tenders)

