import os
import openai

# Load API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

async def summarize_criteria(html_content: str) -> str:
    """
    Given the raw HTML of a TED tender page, calls GPT‑4O‑mini to extract
    and briefly summarize the eligibility & award criteria.
    Returns the cleaned-up summary text.
    """
    system_prompt = (
        "You are an expert in EU procurement. "
        "From the provided HTML of a TED tender notice, meticulously analyze and extract every "
        "eligibility requirement and every award criterion, whether formal, financial, technical, experience levels,etc., then "
        "produce a concise summary -it should be no longer than 1,000 characters, and "
        "categorize the eligibility criteria (e.g., Financial, Technical, Formal etc.) that bidders must fulfil. "
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": html_content}
    ]
    resp = await openai.ChatCompletion.acreate(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.0,
        max_tokens=300,
    )
    summary = resp.choices[0].message.content.strip()
    return summary

