import os
import markdown
from supabase import create_client
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

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

def build_tenders_html(tenders, keyword, cpv):
    intro = f"We heard you are looking for tenders in the <b>{keyword}</b> area under <b>{cpv}</b> category – here you are:<br><br>"
    html = intro
    for tender in tenders:
        summary_md = tender.get('summary', '')
        summary_html = markdown.markdown(summary_md, extensions=['extra', 'nl2br'])
        html += summary_html
        if tender.get('url'):
            html += f'<br><a href="{tender["url"]}" style="color:#1a3767;text-decoration:underline;">Tender link</a><br><br>'
    return (
        "<div style='font-family:Segoe UI,Arial,sans-serif;font-size:16px;line-height:1.7;color:#212121;'>"
        f"{html}"
        "</div>"
    )

def send_tender_email(user_email, tenders, keyword, cpv, first_name=None):
    print("[EMAILER] Preparing to send email...")
    api_key = os.getenv("BREVO_API_KEY")
    if not api_key:
        print("ERROR: BREVO_API_KEY not set in environment variables!")
        raise Exception("BREVO_API_KEY missing")
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = api_key

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    if not first_name:
        first_name = get_user_first_name(user_email)
    tenders_html = build_tenders_html(tenders, keyword, cpv)
    template_id = 1  # <-- set your Brevo template ID

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": user_email, "name": first_name or "User"}],
        template_id=template_id,
        params={
            "first_name": first_name,
            "tenders_html": tenders_html
        }
    )

    try:
        print("[EMAILER] Sending email to", user_email)
        api_response = api_instance.send_transac_email(send_smtp_email)
        print("[EMAILER] Brevo API response:", api_response)
    except ApiException as e:
        print("[EMAILER] Exception when calling Brevo API:", e)
    except Exception as e:
        print("[EMAILER] General error:", e)
