import re

# Regular expressions for identifying sensitive PII data
PII_PATTERNS = [
    # Email addresses (e.g. user@example.com)
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    # Phone numbers (e.g. +1-555-123-4567, (555) 123-4567, 555-987-6543)
    r"\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
    # Credit card numbers (13 to 19 digits with optional spaces or hyphens)
    # Note: Raw string prefix 'r' is mandatory. Without 'r', '\b' is parsed as ASCII Backspace (\x08),
    # which breaks regex word boundary matching and causes credit card detection to fail.
    r"\b(?:\d[ -]*?){13,19}\b",
    # API keys / Bearer tokens (e.g. api_key=sk_live_123456789, token: xyz123)
    r"(?i)\b(api[_\s]?key|bearer|token)\s*[:=]\s*\S+",
    # Passwords (e.g. password=secret123, pwd: mypassword)
    r"(?i)\b(password|passwd|pwd)\s*[:=]\s*\S+",
]


def redact_text(text: str) -> str:
    """
    Scans input text for sensitive PII (emails, phones, credit cards, API keys, passwords)
    and replaces matched sensitive patterns with '[REDACTED]'.
    """
    if not isinstance(text, str):
        return text

    redacted = text
    for pattern in PII_PATTERNS:
        redacted = re.sub(pattern, "[REDACTED]", redacted)

    return redacted

