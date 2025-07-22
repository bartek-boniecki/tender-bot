import os
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

def format_tenders_html(tenders):
    if not tenders:
        return "<p>No tenders were found matching your criteria this week.</p>"

    cards = []
    for t in tenders:
        summary = t.get("summary") or ""
        url = t.get("url") or "#"
        card = f"""
        <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;border:1px solid #e0e0e0;border-radius:10px;background:#fafbfc;">
          <tr>
            <td style="padding:18px 20px 14px 20px;">
              <div style="font-size:18px;font-weight:bold;margin-bottom:8px;">Tender Opportunity</div>
              <div style="margin-bottom:10px;">{summary}</div>
              <a href="{url}" style="display:inline-block;margin-top:8px;font-size:15px;color:#ffffff;background:#176ae5;border-radius:6px;padding:8px 16px;text-decoration:none;">View Tender</a>
            </td>
          </tr>
        </table>
        """
        cards.append(card)
    return "\n".join(cards)

def send_tender_email(user_email, tenders, keyword, cpv, first_name):
    tenders_html = format_tenders_html(tenders)

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = os.getenv("BREVO_API_KEY")
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    template_id = 1  # <-- Replace with your actual Brevo template ID

    params = {
        "first_name": first_name or "User",
        "keyword": keyword,
        "cpv": cpv,
        "tenders_html": tenders_html
    }

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": user_email, "name": first_name or "User"}],
        template_id=template_id,
        params=params,
        sender={"name": "TenderLetter", "email": "noreply@tenderletter.com"}
    )

    try:
        api_instance.send_transac_email(send_smtp_email)
    except ApiException as e:
        print(f"Brevo email exception: {e}")
