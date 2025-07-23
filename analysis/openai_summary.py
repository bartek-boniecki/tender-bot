# analysis/openai_summary.py

import os
import openai
import asyncio
from bs4 import BeautifulSoup

openai.api_key = os.getenv("OPENAI_API_KEY")
MAX_CHARS = 50000

async def summarize_subject_matter(html_content: str) -> str:
    """
    Translate any non‑English parts into English, then produce a single concise
    (≤200 chars) summary focusing on the specific tasks or services the contractor
    will be required to perform.
    """
    # Extract visible text
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    raw = soup.get_text(separator="\n")
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    clean_text = "\n".join(lines)[:MAX_CHARS]

    system_prompt = (
        "You are an expert in EU procurement. From the provided TED tender notice text, "
        "first translate any non‑English passages into English. Then write a single "
        "concise summary (max 200 characters) describing the exact tasks or services "
        "the contractor will perform under this contract. Respond only with that text."
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
        max_tokens=100,
    )
    return resp.choices[0].message.content.strip()


async def summarize_eligibility(html_content: str) -> str:
    """
    Translate into English if needed, then extract all eligibility & award criteria
    and return an HTML snippet with <h3> headings and <ul><li> lists.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    raw = soup.get_text(separator="\n")
    clean_text = "\n".join(ln.strip() for ln in raw.splitlines() if ln.strip())[:MAX_CHARS]

    system_prompt = (
        "You are a procurement expert. From the given TED tender notice text, "
        "translate non‑English passages into English, then extract each eligibility "
        "requirement and award criterion. Output only an HTML snippet:\n"
        "• Use <h3> per category (e.g., Financial Criteria).\n"
        "• Under each, list <ul><li> items.\n"
        "Do NOT include markdown or wrappers—only the inner snippet."
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
