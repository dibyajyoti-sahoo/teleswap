import re

ALERT_RE = re.compile(r'(?:🟢\uFE0F?\s*){2,}|(?:🔴\uFE0F?\s*){2,}', re.UNICODE)

def is_trade_alert(text: str) -> bool:
    """
    Returns True if the message contains the required green or red alert emojis.
    """
    if not text:
        return False
    return bool(ALERT_RE.search(text))