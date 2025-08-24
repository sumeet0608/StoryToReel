import os, re, asyncio, requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import praw
from utils import logger
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USER_AGENT = os.getenv("REDDIT_USER_AGENT", "reelsbot/1.0")

# Check if PRAW credentials are provided
HAS_PRAW = bool(CLIENT_ID and CLIENT_SECRET)

async def extract_text_from_input(message_text: str) -> str:
    payload = message_text.split(" ", 1)[1] if " " in message_text else ""
    payload = payload.strip()
    if is_reddit_url(payload):
        logger.info(f"Attempting to fetch story from URL: {payload}")
        text = fetch_reddit_post(payload)
        logger.info(f"Fetched text: {text}")
        if len(text.strip()) < 50:
            raise RuntimeError("Couldn't extract enough text. The post might be too old or the content is missing.")
        return text
    return payload


def is_reddit_url(s: str) -> bool:
    try:
        u = urlparse(s)
        return ("reddit.com" in u.netloc) and (u.path.startswith("/r/") or u.path.startswith("/comments/"))
    except Exception:
        return False
    

def fetch_reddit_post(url: str) -> str:
    if HAS_PRAW:

        try:
            reddit = praw.Reddit(client_id=CLIENT_ID,
                                 client_secret=CLIENT_SECRET,
                                 user_agent=USER_AGENT)
            submission = reddit.submission(url=url)
            submission.comments.replace_more(limit=0)
            post_text = submission.selftext or ""
            #comments = "\n\n".join(comment.body for comment in submission.comments.list()[:5])
            full_text = f"{submission.title}\n\n{post_text}"
            #\n\nTop Comments:\n{comments}
            return clean_text(full_text.strip())
        except Exception as e:
            logger.error(f"PRAW fetch failed: {e}")
    
    # Fallback to web scraping
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else ''
        post_text_elem = soup.find('div', {'data-test-id': 'post-content'})
        post_text = post_text_elem.get_text("\n", strip=True) if post_text_elem else ''
        # comments_elems = soup.find_all('div', {'data-test-id': 'comment'})
        # comments = "\n\n".join(c.get_text("\n", strip=True) for c in comments_elems[:5])
        full_text = f"{title}\n\n{post_text}"
        #\n\nTop Comments:\n{comments}
        return clean_text(full_text.strip())
    except Exception as e:
        logger.error(f"Web scraping fetch failed: {e}")
        raise ValueError("Failed to fetch Reddit post content.")
    
def clean_text(t: str) -> str:
    """Cleans up the fetched text for TTS processing."""
    t = re.sub(r"Edit:.*$", "", t, flags=re.IGNORECASE)
    # Replace common HTML entities
    t = t.replace("&amp;", "&")

    t = re.sub(r"\s+", " ", t).strip()
    return t