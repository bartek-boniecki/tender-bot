# utils/emailer.py

import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From, To

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
    Sends a transactional email via SendGrid Dynamic Templates.
    Expects these ENV vars:
      - SENDGRID_API_KEY
      - SENDGRID_TEMPLATE_ID
      - FROM_EMAIL
      - FROM_NAME
    """

    api_key     = os.getenv("SENDGRID_API_KEY")
    template_id = os.getenv("SENDGRID_TEMPLATE_ID")
    from_email  = os.getenv("FROM_EMAIL")
    from_name   = os.getenv("FROM_NAME", "")

    if not all([api_key, template_id, from_email]):
        raise RuntimeError(
            "SENDGRID_API_KEY, SENDGRID_TEMPLATE_ID, and FROM_EMAIL must be set"
        )

    # Build the SendGrid Mail object with dynamic template data
    message = Mail(
        from_email=From(from_email, from_name),
        to_emails=To(to_email, first_name=first_name),
    )
    message.template_id = template_id
    message.dynamic_template_data = {
        "first_name": first_name,
        "cpv": cpv,
        "keyword": keyword,
        "tenders": tenders
    }

    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        logger.info(
            f"SendGrid accepted template {template_id} "
            f"status_code={response.status_code} for {to_email}"
        )
        return response
    except Exception:
        logger.exception(f"Failed to send email via SendGrid to {to_email}")
        raise
