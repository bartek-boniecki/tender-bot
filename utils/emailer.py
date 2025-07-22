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
        # Each tender is rendered as a visually separated box (table/card)
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

    # Email subject and body
    subject = f"Your Weekly Tender Matches: {keyword} ({cpv})"
    html_content = f"""
    <div style="font-family:Segoe UI,Arial,sans-serif;font-size:16px;line-height:1.7;color:#212121;max-width:700px;margin:0 auto;">
      <div style="background:#176ae5;padding:18px 20px 10px 20px;border-radius:10px 10px 0 0;">
        <span style="font-size:22px;font-weight:bold;color:#fff;">TenderLetter</span>
      </div>
      <div style="padding:24px 20px 30px 20px;background:#fff;border-radius:0 0 10px 10px;">
        <p>Hi <strong>{first_name}</strong>,</p>
        <p>Here are this week's public tenders for <b>{keyword}</b> (<b>{cpv}</b>):</p>
        {tenders_html}
        <hr style="margin:28px 0 18px 0; border:0; border-top:1px solid #e0e0e0;">
        <div style="font-size:13px;color:#889;">
          You are receiving this because you subscribed for weekly public tenders on TenderLetter.<br>
          <span style="color:#bbb;">{user_email}</span>
        </div>
      </div>
    </div>
    """

    # If you use a Brevo template, you can pass html_content as a param
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": user_email, "name": first_name or "User"}],
        subject=subject,
        html_content=html_content,
        sender={"name": "TenderLetter", "email": "noreply@tenderletter.com"}
    )

    try:
        api_instance.send_transac_email(send_smtp_email)
    except ApiException as e:
        print(f"Brevo email exception: {e}")
