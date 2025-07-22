# analysis/openai_summary.py

import os
import openai
import asyncio

# Load your OpenAI API key; Railway will inject OPENAI_API_KEY into the environment.
openai.api_key = os.getenv("OPENAI_API_KEY")

async def summarize_eligibility(html_content: str) -> str:
    """
    Given the raw HTML of a TED tender page, offload to a thread to call
    the synchronous OpenAI chat completions endpoint, then return the summary.
    """
    system_prompt = (
        "You are an expert in EU procurement. "
        "From the provided HTML of a TED tender notice, meticulously extract every "
        "eligibility requirement and award criterion—formal, financial, technical, "
        "experience, etc.—and produce a concise summary (max 1000 characters), "
        "categorizing criteria by type (Financial, Technical, Formal, etc.)."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": html_content}
    ]

    # Use the modern v1 SDK namespace; offload to a thread so we can await without blocking.
    resp = await asyncio.to_thread(
        openai.chat.completions.create,
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.0,
        max_tokens=300,
    )

    # Extract and return the assistant’s reply
    return resp.choices[0].message.content.strip()
