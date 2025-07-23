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

    Passes through:
      - subject: used in the template's Subject field via {{subject}}
      - first_name, cpv, keyword for greeting
      - tenders: array of {title, subject_matter, url, summary_html}
    """

    api_key     = os.getenv("SENDGRID_API_KEY")
    template_id = os.getenv("SENDGRID_TEMPLATE_ID")
    from_email  = os.getenv("FROM_EMAIL")
    from_name   = os.getenv("FROM_NAME", "")

    if not all([api_key, template_id, from_email]):
        raise RuntimeError(
            "SENDGRID_API_KEY, SENDGRID_TEMPLATE_ID, and FROM_EMAIL must be set"
        )

    # Build the dynamic subject line from the first tender's subject matter
    subject = f"{tenders[0]['subject_matter']}" if tenders else f"Tenders for {keyword}/{cpv}"

    message = Mail(
        from_email=From(from_email, from_name),
        to_emails=To(to_email, name=first_name),
    )

    # Tell SendGrid which Dynamic Template to use
    message.template_id = template_id

    # Note: Dynamic Templates ignore `message.subject`, so we supply it as a parameter
    message.dynamic_template_data = {
        "subject": subject,
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
