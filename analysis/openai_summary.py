# analysis/openai_summary.py

import os
import openai
import asyncio
from bs4 import BeautifulSoup

openai.api_key = os.getenv("OPENAI_API_KEY")
MAX_CHARS = 50000

async def extract_descriptive_title(html_content: str) -> str:
    """
    Use GPT to craft a 5–8‑word English title capturing the substance of the tender,
    ignoring numeric codes. Falls back to the page's <h1> if GPT fails.
    """
    # Fallback from <h1>
    soup = BeautifulSoup(html_content, "html.parser")
    h1 = soup.find("h1")
    fallback = h1.get_text().strip() if h1 else "Tender Notice"

    # Truncate input
    text = soup.get_text(separator="\n")
    text = "\n".join(line.strip() for line in text.splitlines() if line.strip())[:MAX_CHARS]

    system = (
        "You are an expert in EU public tenders. From the provided tender notice HTML, "
        "generate a **5–8 word** English title that clearly conveys what the contract is for, "
        "omitting any codes or reference numbers. Reply _only_ with the title."
    )
    messages = [{"role":"system","content":system}, {"role":"user","content":text}]

    try:
        resp = await asyncio.to_thread(
            openai.chat.completions.create,
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.0,
            max_tokens=16,
        )
        title = resp.choices[0].message.content.strip()
        return title or fallback
    except Exception:
        return fallback

async def summarize_subject_matter(html_content: str) -> str:
    """
    Always in English: translate non-English parts, then give a ≤200‑char summary
    of _what the contractor will do_ under this tender.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["script","style"]): tag.decompose()
    text = soup.get_text(separator="\n")
    clean = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    if len(clean) > MAX_CHARS: clean = clean[:MAX_CHARS]

    system = (
        "You are an expert in EU procurement. The following is tender notice text "
        "(may contain multiple languages). First translate any non‑English passages "
        "into English. Then produce a single concise summary (≤200 characters) "
        "explaining exactly what work the contractor will be required to perform. "
        "Reply _only_ with that summary in English."
    )
    messages = [{"role":"system","content":system}, {"role":"user","content":clean}]

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
    Always in English: translate non-English parts, then extract eligibility & award criteria
    and output a clean HTML snippet with <h3> headings and <ul><li> lists.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["script","style"]): tag.decompose()
    text = soup.get_text(separator="\n")
    clean = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    if len(clean) > MAX_CHARS: clean = clean[:MAX_CHARS]

    system = (
        "You are an EU procurement specialist. The input is the full text of a tender notice. "
        "First translate any non‑English passages into English, then extract _all_ eligibility "
        "requirements and award criteria. Return _only_ an HTML fragment:\n"
        "- Use <h3>Category Name</h3>\n"
        "- Under each, wrap each item in <ul><li>…</li></ul>\n"
        "No markdown, no asterisks, no <html>/<body> wrappers—pure inner snippet."
    )
    messages = [{"role":"system","content":system}, {"role":"user","content":clean}]

    resp = await asyncio.to_thread(
        openai.chat.completions.create,
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.0,
        max_tokens=500,
    )
    return resp.choices[0].message.content.strip()
