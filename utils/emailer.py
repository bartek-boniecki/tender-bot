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

    Passes:
      - subject: static, generic weekly digest title
      - first_name, cpv, keyword for greeting
      - tenders: array of {title, subject_matter, url, summary}
    """

    api_key     = os.getenv("SENDGRID_API_KEY")
    template_id = os.getenv("SENDGRID_TEMPLATE_ID")
    from_email  = os.getenv("FROM_EMAIL")
    from_name   = os.getenv("FROM_NAME", "")

    if not all([api_key, template_id, from_email]):
        raise RuntimeError(
            "SENDGRID_API_KEY, SENDGRID_TEMPLATE_ID, and FROM_EMAIL must be set"
        )

    # 1) Use a clear, static weekly digest subject
    email_subject = "EU TenderBot Weekly Summary"

    # 2) Construct the SendGrid Mail object
    message = Mail(
        from_email=From(from_email, from_name),
        to_emails=To(to_email, name=first_name),
    )
    message.template_id = template_id

    # 3) Supply all dynamic data, including the static subject
    message.dynamic_template_data = {
        "subject":      email_subject,
        "first_name":   first_name,
        "cpv":          cpv,
        "keyword":      keyword,
        "tenders":      tenders
    }

    try:
        sg = SendGridAPIClient(api_key)
        resp = sg.send(message)
        logger.info(
            f"SendGrid accepted template {template_id} "
            f"status_code={resp.status_code} for {to_email}"
        )
        return resp
    except Exception:
        logger.exception(f"Failed to send email via SendGrid to {to_email}")
        raise
