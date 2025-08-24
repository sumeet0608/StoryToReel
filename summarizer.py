import re
from utils import logger

def make_reel_script_prompt(raw_text: str) -> str:
    raw = raw_text.strip()
    raw = re.sub(r"\s+", " ", raw)

    persona = """Summarize the following story as a dramatic and slightly over-the-top gossip columnist. Give it some sizzle. Make it a bit engaging and funny for viewers of instagram reels.""" 

    prompt = f"""{persona}\n{raw}"""

    return prompt