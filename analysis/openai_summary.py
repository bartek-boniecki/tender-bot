from openai import OpenAI
from bs4 import BeautifulSoup
import os

def summarize_eligibility(html: str) -> str:
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "[No summary available - error: OPENAI_API_KEY not set]"

        client = OpenAI(api_key=api_key)
        soup = BeautifulSoup(html, "html.parser")
        raw_text = soup.get_text(separator="\n", strip=True)
        content = raw_text[:12000]

        prompt = (
            "Thoroughly analyze full text and every part of the EU public tender notice. "
            "Your task is to extract all the participation, eigibility or selection criteria** that a bidder must fulfill. "
            "If any part of the text is in another language, translate and summarize in English. "
            "Include any criterion, whether formal, financial, technical, references, experience levels, staff qualifications, legal, or technical conditions. "
            "Summary should be no longer than 1,500 characters per one tender, and categorize the eligibility criteria (e.g., Financial, Technical, Legal etc.). "
            "Any Legal criteria should be no longer than 200 characters"
            "If specific values or documents are required, list them precisely."            
            f"\n\n{content}"
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a tender analyst specialized in extracting bidder eligibility requirements from procurement notices."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("OpenAI summary exception:", type(e), e)
        return f"[No summary available - error: {type(e).__name__}: {e}]"