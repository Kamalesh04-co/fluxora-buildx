import requests
import xml.etree.ElementTree as ET
import urllib.parse
from config import OLLAMA_MODEL, OLLAMA_URL

def get_live_maritime_and_political_news(region: str = "Indian Ocean, Bay of Bengal, Cochin, Colombo, Red Sea") -> str:
    """Fetches real-time Google News RSS headlines and summarizes them locally via Ollama."""
    try:
        clean_region = " OR ".join([r.strip() for r in region.split(",") if r.strip()])
        query = urllib.parse.quote(f"(shipping OR port OR maritime OR cyclone) ({clean_region})")
        rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"

        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(rss_url, headers=headers, timeout=15)
        root = ET.fromstring(res.content)

        headlines = []
        for item in root.findall(".//item")[:6]:
            title = item.find("title").text
            pub_date = item.find("pubDate").text[:16] if item.find("pubDate") is not None else ""
            headlines.append(f"• [{pub_date}] {title}")

        if not headlines:
            return "⚠️ No recent RSS articles matched. Try a broader region like 'Indian Ocean, Red Sea'."

        raw_news = "\n".join(headlines)

        try:
            summary_prompt = (
                f"Summarize these maritime & geopolitical news headlines into 4 very short bullet points:\n{raw_news}"
            )
            ollama_res = requests.post(
                OLLAMA_URL,
                json={"model": OLLAMA_MODEL, "prompt": summary_prompt, "stream": False},
                timeout=90
            )
            if ollama_res.status_code == 200:
                summary = ollama_res.json().get("response", "").strip()
                return f"{summary}\n\n--- Live Google News Headlines ---\n{raw_news}"
        except Exception:
            pass

        return f"--- Live Google News Headlines ---\n{raw_news}"
    except Exception as e:
        return f"⚠️ Live News Fetch Error: {str(e)}"
