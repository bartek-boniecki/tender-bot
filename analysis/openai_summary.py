# analysis/openai_summary.py

import os
import openai
import asyncio
from bs4 import BeautifulSoup

# Load your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Maximum chars to send to the model to avoid context limits
MAX_CHARS = 50000

async def summarize_eligibility(html_content: str) -> str:
    """
    Extract every eligibility requirement and award criterion from a TED tender notice,
    grouping by category only when there are multiple items in that category.
    Returns a concise HTML fragment:
      - For categories with >1 item: <h3>Category</h3><ul><li>…</li>…</ul>
      - For single items: just <ul><li>…</li></ul>
    Always in English, no markdown, no wrappers.
    """
    # 1) Strip scripts/styles and get clean text
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    raw = soup.get_text(separator="\n")
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    clean_text = "\n".join(lines)[:MAX_CHARS]

    # 2) Craft system prompt for structured grouping
    system_prompt = """
You are an expert in EU procurement. The input is the full text of a TED tender notice.
1) Translate any non‑English passages into English.
2) Extract every eligibility requirement AND every award criterion.
3) Organize them as follows:
   - If a category (Formal, Financial, Technical, Experience) has multiple items, output:
       <h3>Financial Criteria</h3>
       <ul><li>First item</li><li>Second item</li></ul>
   - If a category has only one item, output only:
       <ul><li>The single item</li></ul>
       (i.e., no <h3> header for that category)
4) Do NOT include markdown, asterisks, or any <html>/<body> wrappers—return only the inner HTML snippet.
5) Keep it as brief as possible while capturing all criteria.
Respond in English.
    """.strip()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": clean_text}
    ]

    # 3) Call the model in a background thread
    resp = await asyncio.to_thread(
        openai.chat.completions.create,
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.0,
        max_tokens=500,
    )

    return resp.choices[0].message.content.strip()
