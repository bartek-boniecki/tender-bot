import os
import openai

# Load the API key (Railway will inject OPENAI_API_KEY automatically)
openai.api_key = os.getenv("OPENAI_API_KEY")

async def summarize_eligibility(html_content: str) -> str:
    """
    Given the raw HTML of a TED tender page, calls GPT‑4O‑mini to extract
    and briefly summarize all eligibility requirements and award criteria.
    Returns the cleaned-up summary text.
    """
    system_prompt = (
        "You are an expert in EU procurement. "
        "From the provided HTML of a TED tender notice, meticulously analyze and extract every "
        "eligibility requirement and every award criterion—formal, financial, technical, experience, etc.—"
        "then produce a concise summary (max 1000 characters), categorizing criteria "
        "by type (e.g., Financial, Technical, Formal)."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": html_content}
    ]

    # ← Migrate to v1 interface
    resp = await openai.chat.completions.acreate(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.0,
        max_tokens=300,
    )

    # Extract and return the assistant’s reply
    summary = resp.choices[0].message.content.strip()
    return summary
