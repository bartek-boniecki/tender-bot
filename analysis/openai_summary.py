# analysis/openai_summary.py

import os
import openai
import asyncio
from bs4 import BeautifulSoup

# Load your OpenAI key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Maximum raw text chars to send to the model
MAX_CHARS = 50000

async def extract_descriptive_title(html_content: str) -> str:
    """
    Calls GPT to produce a max‑10‑word descriptive title for the tender,
    ignoring reference numbers. Falls back to the HTML <h1> if the call fails.
    """
    # First try to pull <h1> from the page
    soup = BeautifulSoup(html_content, "html.parser")
    h1 = soup.find("h1")
    fallback = h1.get_text().strip() if h1 else "Tender Notice"

    system_prompt = (
        "You are an expert in EU procurement. "
        "From the provided HTML of a TED tender notice, produce a single concise title "
        "(no more than 10 words) that captures the substance of the tender. "
        "Ignore any numeric reference codes. Respond only with the English title text."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": html_content[:MAX_CHARS]}
    ]

    try:
        resp = await asyncio.to_thread(
            openai.chat.completions.create,
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.0,
            max_tokens=20,
        )
        title = resp.choices[0].message.content.strip()
        return title or fallback
    except Exception:
        return fallback

async def summarize_eligibility(html_content: str) -> str:
    """
    Extract visible text, truncate, and call GPT to return an HTML snippet
    of eligibility & award criteria—always in English.
    """
    # 1) Strip scripts/styles
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    raw_text = soup.get_text(separator="\n")

    # 2) Clean & truncate
    lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]
    clean_text = "\n".join(lines)
    if len(clean_text) > MAX_CHARS:
        clean_text = clean_text[:MAX_CHARS]

    # 3) Prompt GPT for HTML snippet, forcing English translation if needed
    system_prompt = (
        "You are a procurement expert. The following is the text of a TED tender notice, "
        "which may include non‑English passages. First **translate any non‑English parts** "
        "into English. Then extract every eligibility requirement and award criterion, "
        "and output a clean HTML snippet:\n"
        "- Use <h3> for each category (e.g., Financial Criteria).\n"
        "- Under each, use a <ul> of <li> items.\n"
        "- Do NOT include markdown or asterisks—only HTML.\n"
        "Return only the snippet (no <html>/<body> wrappers). Always respond in English."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": clean_text}
    ]

    resp = await asyncio.to_thread(
        openai.chat.completions.create,
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.0,
        max_tokens=500,
    )
    return resp.choices[0].message.content.strip()
