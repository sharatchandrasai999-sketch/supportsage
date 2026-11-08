"""Core triage logic: keyword classification, priority, draft replies."""

TRIAGE_NOTE = "mock rule-based triage, no LLM call"

# Keywords checked against the lowercased subject + body.
CATEGORY_KEYWORDS = {
    "billing": ["invoice", "charge", "refund", "payment", "price"],
    "technical": ["error", "crash", "bug", "broken", "not working", "slow"],
    "account": ["login", "password", "reset", "access", "profile"],
}

URGENT_WORDS = [
    "urgent",
    "asap",
    "down",
    "outage",
    "cannot access",
    "charged twice",
    "data loss",
]

# Reply template per category: 2-3 sentences, names the subject, gives a next step.
DRAFT_TEMPLATES = {
    "billing": (
        "Thanks for writing about '{subject}' — this looks like a billing question, "
        "so I've flagged it for the billing team. "
        "As a next step, please reply with the invoice number or the last four digits "
        "of the card used and we'll check the charge for you."
    ),
    "technical": (
        "Sorry you're running into trouble with '{subject}'. "
        "I've logged this as a technical issue for the support team to investigate. "
        "As a next step, please share any error message you see and the steps that "
        "lead to the problem so we can reproduce it."
    ),
    "account": (
        "Thanks for reaching out about '{subject}'. "
        "I've flagged this as an account issue. "
        "As a next step, please try the password-reset link on the sign-in page, and "
        "if that doesn't work, reply with the email address on the account."
    ),
    "other": (
        "Thanks for writing about '{subject}'. "
        "I've passed your message to the support team. "
        "As a next step, please reply with any extra detail that would help us "
        "understand what you need."
    ),
}


def classify(text):
    """Return billing / technical / account / other by keyword hits.

    The category with the most keyword matches wins; ties break in the
    order billing, technical, account. No match means "other".
    """
    text = text.lower()
    best_category = "other"
    best_hits = 0
    for category, keywords in CATEGORY_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in text)
        if hits > best_hits:
            best_hits = hits
            best_category = category
    return best_category


def priority_for(category, text):
    """Return high / medium / low.

    High: any urgent word, or a technical ticket mentioning crash/outage.
    Medium: billing or account. Low: everything else.
    """
    text = text.lower()
    if any(word in text for word in URGENT_WORDS):
        return "high"
    if category == "technical" and ("crash" in text or "outage" in text):
        return "high"
    if category in ("billing", "account"):
        return "medium"
    return "low"


def draft_reply(category, subject):
    """Templated draft reply for the category, referencing the subject."""
    return DRAFT_TEMPLATES[category].format(subject=subject)


def triage_ticket(ticket):
    """Triage one ticket dict; returns a new dict with triage fields added."""
    subject = ticket.get("subject", "")
    body = ticket.get("body", "")
    text = f"{subject} {body}"
    category = classify(text)
    return {
        **ticket,
        "category": category,
        "priority": priority_for(category, text),
        "draft_reply": draft_reply(category, subject),
        "triage_note": TRIAGE_NOTE,
    }
