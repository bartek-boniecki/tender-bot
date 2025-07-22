# utils/emailer.py

import os
import logging
import httpx

logger = logging.getLogger("tender-bot.emailer")
logging.basicConfig(level=logging.INFO)

def send_tender_email(
    to_email: str,
    tenders: list[dict],
    keyword: str,
    cpv: str,
    first_name: str
):
    """
    Sends a transactional email using a Brevo template,
    passing tenders as a single HTML snippet in `tendersHtml`.

    ENV vars required:
      - BREVO_API_KEY
      - BREVO_TEMPLATE_ID
    Your Brevo template should include {{{tendersHtml}}} to render the list.
    """

    api_key     = os.getenv("BREVO_API_KEY")
    template_id = os.getenv("BREVO_TEMPLATE_ID")

    if not api_key or not template_id:
        raise RuntimeError("BREVO_API_KEY and BREVO_TEMPLATE_ID must be set")

    # Build HTML list of tenders
    if tenders:
        list_items = "".join(
            f"<li><a href=\"{t['url']}\">{t['url']}</a><p>{t['summary']}</p></li>"
            for t in tenders
        )
        tenders_html = f"<ul>{list_items}</ul>"
    else:
        tenders_html = "<p>No tenders found.</p>"

    # Parameters sent into your Brevo template
    params = {
        "firstName": first_name,
        "cpv": cpv,
        "keyword": keyword,
        "tendersHtml": tenders_html
    }

    payload = {
        "to": [{"email": to_email, "name": first_name}],
        "templateId": int(template_id),
        "params": params
    }

    headers = {
        "api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    url = "https://api.brevo.com/v3/smtp/email"

    try:
        resp = httpx.post(url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        msg_id = data.get("messageId", "<unknown>")
        logger.info(f"Brevo accepted template email id={msg_id} for {to_email}")
        return data
    except Exception:
        logger.exception(f"Failed to send templated email to {to_email}")
        raise
