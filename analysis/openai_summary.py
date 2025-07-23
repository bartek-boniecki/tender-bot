# analysis/openai_summary.py

import os
import openai
import asyncio
from bs4 import BeautifulSoup

# Load your OpenAI key; Railway will inject OPENAI_API_KEY automatically.
openai.api_key = os.getenv("OPENAI_API_KEY")

# Truncate raw text to stay under model context limits
MAX_CHARS = 50000

async def summarize_eligibility(html_content: str) -> str:
    """
    1) Strips out scripts/styles and extracts visible text
    2) Cleans, de‑dupes lines, and truncates to MAX_CHARS
    3) Calls GPT-4O‑mini with instructions to output HTML:
       - Use <h3> headings for each category (Financial, Technical, Award)
       - Under each, use a <ul> with <li> items for criteria
       - No markdown or asterisks—pure HTML snippet only
    Returns that HTML snippet as a string.
    """
    # 1) Extract visible text
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    raw_text = soup.get_text(separator="\n")

    # 2) Clean & truncate
    lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]
    clean_text = "\n".join(lines)
    if len(clean_text) > MAX_CHARS:
        print(
            f"[openai_summary] Truncating input from {len(clean_text)} "
            f"to {MAX_CHARS} chars to avoid overflow."
        )
        clean_text = clean_text[:MAX_CHARS]

    # 3) Prompt GPT to emit HTML
    system_prompt = (
        "You are an expert in EU procurement. "
        "From the provided TED tender text, extract every eligibility requirement "
        "and every award criterion, then output a single HTML snippet:\n\n"
        "  • Use an <h3> heading for each category, e.g. <h3>Financial Criteria</h3>.\n"
        "  • Under each heading, list each point as a <ul> with <li> items.\n"
        "  • Do NOT include any markdown, asterisks, or other markup—only HTML.\n"
        "  • Do NOT wrap in <html> or <body> tags; return only the inner snippet.\n"
    )
    messages = [
        {"role": "system",  "content": system_prompt},
        {"role": "user",    "content": clean_text}
    ]

    # Call the sync .create via a thread to keep FastAPI responsive
    resp = await asyncio.to_thread(
        openai.chat.completions.create,
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.0,
        max_tokens=500,
    )

    html_snippet = resp.choices[0].message.content.strip()
    return html_snippet
