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
    Sends a transactional email using a pre‐configured Brevo template.
    All template defaults (sender, subject, body) are taken from Brevo.
    Expects these ENV vars:
      - BREVO_API_KEY
      - BREVO_TEMPLATE_ID
    And assumes your template defines placeholders:
      {{ firstName }}, {{ cpv }}, {{ keyword }}, and {{ tenders }} 
      (where tenders is a list of {url,summary} objects).
    """

    api_key     = os.getenv("BREVO_API_KEY")
    template_id = os.getenv("BREVO_TEMPLATE_ID")

    if not api_key or not template_id:
        raise RuntimeError("BREVO_API_KEY and BREVO_TEMPLATE_ID must be set")

    # Build the params payload for your template
    params = {
        "firstName": first_name,
        "cpv": cpv,
        "keyword": keyword,
        "tenders": tenders
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
    except Exception as e:
        logger.exception(f"Failed to send templated email to {to_email}")
        raise
