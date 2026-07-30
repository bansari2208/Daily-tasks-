"""
Centralized Decoding & Sampling Configuration for Ticket Classifier.
"""

TEMPERATURE = 0.0
TOP_P = 0.7
MAX_TOKENS = 150
JSON_MODE = True
SCHEMA_VALIDATION = True
CONFIDENCE_THRESHOLD = 0.80

# Centralized Model Configurations
STANDARD_MODEL = "GPT-4.1 Nano"
REASONING_MODEL = "o3-mini"
