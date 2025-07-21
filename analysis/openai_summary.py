from openai import OpenAI
from bs4 import BeautifulSoup
import os

def summarize_eligibility(html: str) -> str:
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "[No summary available - error: OPENAI_API_KEY environment variable not set]"

        # Optional: Print to logs (safe if you only show start/end of key)
        print(f"Loaded OpenAI API key: {api_key[:6]}...{api_key[-4:]}" if api_key else "No OpenAI key found.")

        client = OpenAI(api_key=api_key)
        soup = BeautifulSoup(html, "html.parser")
        raw_text = soup.get_text(separator="\n", strip=True)

        # Cleaned and trimmed content
        content = raw_text[:12000]  # Cap input for token limit

        prompt = (
            "Thoroughly analyze full text and every part of the EU public tender notice. "
            "Your task is to extract all the participation, eigibility or selection criteria** that a bidder must fulfill. "
            "If any part of the text is in another language, translate and summarize in English. "
            "Include any criterion, whether formal, financial, technical, references, experience levels, staff qualifications, legal, or technical conditions. "
            "Summarize as briefly as possible and categorize the eligibility criteria (e.g., Financial, Technical, Legal, etc.). "
            "If specific values or documents are required, list them precisely.\n\n"
            f"{content}"
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a legal analyst specialized in extracting bidder eligibility requirements from procurement notices."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        import traceback
        print("OpenAI summary exception:", type(e), e)
        return f"[No summary available - error: {type(e).__name__}: {e}]"
