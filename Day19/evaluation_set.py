"""
Day 19 - Fixed Evaluation Dataset Module.

Defines a fixed evaluation set of 20 customer support tickets across 4 balanced categories:
- Billing (5 examples)
- Technical (5 examples)
- Account (5 examples)
- General (5 examples)
"""

from typing import List, Dict, Any

EVALUATION_DATASET: List[Dict[str, Any]] = [
    # --- Category: Billing (5 items) ---
    {
        "id": 1,
        "text": "I was charged twice on my credit card for invoice #4920. Please refund the duplicate $49.99 transaction.",
        "expected_category": "Billing",
        "description": "Duplicate payment charge refund request"
    },
    {
        "id": 2,
        "text": "My monthly subscription auto-renewed yesterday but I want to downgrade to the basic plan and get a prorated credit.",
        "expected_category": "Billing",
        "description": "Subscription downgrade and prorated credit request"
    },
    {
        "id": 3,
        "text": "Payment failed during checkout with error code 502. Card issuer says funds are available.",
        "expected_category": "Billing",
        "description": "Checkout payment failure inquiry"
    },
    {
        "id": 4,
        "text": "Where can I download my annual tax invoice and VAT receipt for fiscal year 2025?",
        "expected_category": "Billing",
        "description": "Tax invoice and receipt download inquiry"
    },
    {
        "id": 5,
        "text": "Unauthorized billing charge of $199 appeared on my statement after canceling last month.",
        "expected_category": "Billing",
        "description": "Post-cancellation unauthorized charge dispute"
    },

    # --- Category: Technical (5 items) ---
    {
        "id": 6,
        "text": "The API endpoint returns HTTP 500 Internal Server Error whenever I POST JSON payloads larger than 5MB.",
        "expected_category": "Technical",
        "description": "API 500 error on large payload submission"
    },
    {
        "id": 7,
        "text": "Database connection pools timeout after 30 seconds of high concurrency on server cluster B.",
        "expected_category": "Technical",
        "description": "Database connection pool timeout under load"
    },
    {
        "id": 8,
        "text": "Webhooks fail to deliver signatures with error SSL handshake failed on port 443.",
        "expected_category": "Technical",
        "description": "Webhook SSL handshake failure"
    },
    {
        "id": 9,
        "text": "The desktop application crashes immediately upon launch on Windows 11 ARM architecture.",
        "expected_category": "Technical",
        "description": "Application crash on Windows 11 ARM startup"
    },
    {
        "id": 10,
        "text": "Latency increased by 400ms after applying patch 2.4.1 to the Redis caching service.",
        "expected_category": "Technical",
        "description": "Redis cache latency degradation post-patch"
    },

    # --- Category: Account (5 items) ---
    {
        "id": 11,
        "text": "I lost my two-factor authentication recovery code and cannot log in to my admin account.",
        "expected_category": "Account",
        "description": "2FA recovery code loss and lockout"
    },
    {
        "id": 12,
        "text": "Please update the primary email address on my enterprise account from dev@oldcompany.com to dev@newcompany.com.",
        "expected_category": "Account",
        "description": "Primary account email change request"
    },
    {
        "id": 13,
        "text": "My account has been locked due to multiple failed password attempts. Please unlock it.",
        "expected_category": "Account",
        "description": "Locked account unlock request"
    },
    {
        "id": 14,
        "text": "How do I transfer ownership of our organization workspace to a new administrator?",
        "expected_category": "Account",
        "description": "Workspace ownership transfer request"
    },
    {
        "id": 15,
        "text": "Single Sign-On (SSO) integration via Okta is throwing SAML assertion validation error.",
        "expected_category": "Account",
        "description": "SAML SSO login assertion failure"
    },

    # --- Category: General (5 items) ---
    {
        "id": 16,
        "text": "What are your standard business operating hours and weekend customer support availability?",
        "expected_category": "General",
        "description": "Business operating hours inquiry"
    },
    {
        "id": 17,
        "text": "Can you provide product roadmap information for upcoming Q4 enterprise features?",
        "expected_category": "General",
        "description": "Product feature roadmap inquiry"
    },
    {
        "id": 18,
        "text": "Where can I read your corporate privacy policy and GDPR compliance documentation?",
        "expected_category": "General",
        "description": "Privacy policy and GDPR documentation request"
    },
    {
        "id": 19,
        "text": "Thank you for the quick help earlier today, everything is working great now!",
        "expected_category": "General",
        "description": "Courtesy thank-you message"
    },
    {
        "id": 20,
        "text": "Do you offer educational or non-profit discounts for university research teams?",
        "expected_category": "General",
        "description": "Non-profit discount policy inquiry"
    },
]


def get_evaluation_set() -> List[Dict[str, Any]]:
    """Returns copy of the fixed 20-item evaluation dataset."""
    return list(EVALUATION_DATASET)
