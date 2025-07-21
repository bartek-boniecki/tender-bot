import os
from supabase import create_client
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import markdown  # <--- Add this!

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
    intro = f"We heard you are looking for tenders in the <b>{keyword}</b> area under <b>{cpv}</b> category - here you are:<br><br>"
    html = ""
    for tender in tenders:
        summary = tender.get('summary', '')
        # Use markdown conversion!
        summary_html = markdown.markdown(summary, extensions=['extra'])
        # Add link at the end
        if tender.get('url'):
            summary_html += f'<br><a href="{tender["url"]}" style="color:#1a3767;text-decoration:underline;">Tender link</a><br><br>'
        html += summary_html
    # Wrap everything in a styled <div>
    return (
        "<div style='font-family:Segoe UI,Arial,sans-serif;font-size:16px;line-height:1.7;color:#212121;'>"
        f"{intro}{html}"
        "</div>"
    )

def send_tender_email(user_email, tenders, keyword, cpv):
    # Use Brevo API to send email
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = os.getenv("BREVO_API_KEY")

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    first_name = get_user_first_name(user_email)
    tenders_html = build_tenders_html(tenders, keyword, cpv)

    # Replace TEMPLATE_ID with your real template ID from Brevo
    template_id = 1  # <--- CHANGE THIS

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

