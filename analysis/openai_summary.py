# analysis/openai_summary.py

import os
import openai
import asyncio
from bs4 import BeautifulSoup

openai.api_key = os.getenv("OPENAI_API_KEY")
MAX_CHARS = 50000

async def summarize_subject_matter(html_content: str) -> str:
    """
    Translate any non‑English parts to English, then produce a concise
    (≤200 chars) summary of the tender’s subject matter.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    clean_text = "\n".join(lines)
    if len(clean_text) > MAX_CHARS:
        clean_text = clean_text[:MAX_CHARS]

    system_prompt = (
        "You are an expert in EU procurement. From the provided TED tender notice text, "
        "first translate any non‑English passages into English, then write a single "
        "concise summary (max 200 characters) describing the subject matter of this tender. "
        "Respond only with that summary text."
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
    Translate to English if needed, then extract and return an HTML snippet
    of eligibility & award criteria using <h3> and <ul><li>.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    clean_text = "\n".join(lines)
    if len(clean_text) > MAX_CHARS:
        clean_text = clean_text[:MAX_CHARS]

    system_prompt = (
        "You are a procurement expert. From the provided TED tender notice text, "
        "translate any non‑English passages into English, then extract every eligibility "
        "requirement and award criterion. Output only an HTML snippet:\n"
        "- Use <h3> for each category (e.g., Financial Criteria).\n"
        "- Under each, list items with <ul><li>.\n"
        "Do not include markdown or extra wrappers—only the snippet."
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
