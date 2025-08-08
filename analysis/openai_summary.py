import os
import openai
import asyncio
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tender-bot.summary")

openai.api_key = os.getenv("OPENAI_API_KEY")
MAX_CHARS = 50000

async def extract_descriptive_title(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")
    h1 = soup.find("h1")
    fallback = h1.get_text().strip() if h1 else "Tender Notice"
    try:
        text = "\n".join(ln.strip() for ln in soup.get_text(separator="\n").splitlines() if ln.strip())[:MAX_CHARS]
        system = (
            "You are an expert in EU tenders. Generate a 5–8 word English title "
            "conveying what the contract is for, omitting any codes. Reply only with the title."
        )
        resp = await asyncio.to_thread(
            openai.chat.completions.create,
            model="gpt-4o-mini",
            messages=[{"role":"system","content":system}, {"role":"user","content":text}],
            temperature=0.0, max_tokens=16
        )
        title = resp.choices[0].message.content.strip()
        return title or fallback
    except Exception as e:
        logger.exception("Title extraction failed")
        return fallback

async def summarize_subject_matter(html_content: str) -> str:
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        text = "\n".join(ln.strip() for ln in soup.get_text(separator="\n").splitlines() if ln.strip())[:MAX_CHARS]
        system = (
            "You are an EU procurement expert. Translate any non‑English text, then write a single concise (≤200 chars) English summary of what work the contractor will perform. "
            "Don't indicate whether the text was translated and don't use asterisks. "
        )
        resp = await asyncio.to_thread(
            openai.chat.completions.create,
            model="gpt-4o-mini",
            messages=[{"role":"system","content":system}, {"role":"user","content":text}],
            temperature=0.0, max_tokens=100
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        logger.exception("Subject‑matter summarization failed")
        return ""

async def summarize_eligibility(html_content: str) -> str:
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        for tag in soup(["script","style"]): tag.decompose()
        clean = "\n".join(ln.strip() for ln in soup.get_text(separator="\n").splitlines() if ln.strip())[:MAX_CHARS]
        system = """
You are an EU procurement specialist. Translate non‑English text, then extract every eligibility requirement and selection criteria for the bidder. 
Briefly present all the criteria (no more than 500 characters in total). 
If possible, group eligibility requirements or selection criteria by categories like formal, financial, technical, experience, etc. 
If a category has >1 item, use:
  <h3>Category</h3><ul><li>…</li></ul>
If only one, just:
  <ul><li>…</li></ul>
Return only that HTML fragment, with no markdown or wrappers.
""".strip()
        resp = await asyncio.to_thread(
            openai.chat.completions.create,
            model="gpt-4o-mini",
            messages=[{"role":"system","content":system}, {"role":"user","content":clean}],
            temperature=0.0, max_tokens=500
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        logger.exception("Eligibility summarization failed")
        return ""
