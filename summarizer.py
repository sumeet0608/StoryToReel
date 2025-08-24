import re

_sum = None

def make_reel_script(raw_text: str, target_words: int = 175) -> str:
    raw = raw_text.strip()
    raw = re.sub(r"\s+", " ", raw)