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
    Calls Brevo's /v3/smtp/email endpoint using a template.
    Your Brevo template must use {{{ params.tenders_html }}} to render the list.
    """

    api_key     = os.getenv("BREVO_API_KEY")
    template_id = os.getenv("BREVO_TEMPLATE_ID")
    if not api_key or not template_id:
        raise RuntimeError("BREVO_API_KEY and BREVO_TEMPLATE_ID must be set")

    # 1) Build the raw HTML list
    if tenders:
        items = "".join(
            f"<li><a href=\"{t['url']}\">{t['url']}</a><p>{t['summary']}</p></li>"
            for t in tenders
        )
        tenders_html = f"<ul>{items}</ul>"
    else:
        tenders_html = "<p>No tenders found.</p>"

    # 2) Prepare the payload for the template
    payload = {
        "to": [{ "email": to_email, "name": first_name }],
        "templateId": int(template_id),
        "params": {
            "first_name": first_name,
            "cpv": cpv,
            "keyword": keyword,
            "tenders_html": tenders_html
        }
    }

    headers = {
        "api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    url = "https://api.brevo.com/v3/smtp/email"

    try:
        resp = httpx.post(url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        logger.info(f"Brevo accepted template email id={data.get('messageId')} for {to_email}")
        return data
    except Exception:
        logger.exception(f"Failed to send templated email to {to_email}")
        raise
