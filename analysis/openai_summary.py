# analysis/openai_summary.py

import os
import openai
import asyncio
from bs4 import BeautifulSoup

# Load your OpenAI API key; Railway will set OPENAI_API_KEY automatically.
openai.api_key = os.getenv("OPENAI_API_KEY")

# How many characters of plain text to send at most:
MAX_CHARS = 50000

async def summarize_eligibility(html_content: str) -> str:
    """
    Given raw TED tender HTML, this:
      1) Parses and extracts visible text only
      2) Cleans and truncates to MAX_CHARS
      3) Calls the OpenAI chat completion endpoint in a thread
      4) Returns the assistant’s summary
    """
    # 1) Extract visible text
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text(separator="\n")

    # 2) Clean up whitespace & empty lines
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    clean_text = "\n".join(lines)

    # 3) Truncate if too long
    if len(clean_text) > MAX_CHARS:
        print(
            f"[openai_summary] Truncating input from {len(clean_text)} "
            f"to {MAX_CHARS} characters to avoid context overflow."
        )
        clean_text = clean_text[:MAX_CHARS]

    # Build messages
    system_prompt = (
        "You are an expert in EU procurement. From the provided TED tender text, "
        "extract every eligibility requirement and award criterion—formal, financial, "
        "technical, experience, etc.—and produce a concise summary (max 1000 characters), "
        "categorizing criteria by type (Financial, Technical, Formal, etc.)."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": clean_text}
    ]

    # 4) Call the modern v1 SDK in a thread so we can await it without blocking
    resp = await asyncio.to_thread(
        openai.chat.completions.create,
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.0,
        max_tokens=300,
    )

    # Return the assistant's reply
    return resp.choices[0].message.content.strip()
