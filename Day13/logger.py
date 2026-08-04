"""
Day 13 Structured Validation Logger.
Logs validation events and self-repair attempts to Day13/logs/day13_validation.jsonl.
"""

import os
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional

LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "logs"))
LOG_FILE = os.path.join(LOG_DIR, "day13_validation.jsonl")


class StructuredValidationLogger:
    """JSONL Logger for boundary validation and self-repair retries."""

    def __init__(self, log_path: str = LOG_FILE):
        self.log_path = log_path
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def log_validation_event(
        self,
        ticket_id: Optional[int],
        retry_number: int,
        validation_error: str,
        error_type: str,
        status: str,
        extra: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Appends a structured log entry to the JSONL log file."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ticket_id": ticket_id,
            "retry_number": retry_number,
            "validation_error": validation_error,
            "error_type": error_type,
            "status": status
        }
        if extra:
            entry["extra"] = extra

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

        return entry

    def read_all_logs(self):
        """Reads and parses all logged records."""
        if not os.path.exists(self.log_path):
            return []
        records = []
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line.strip()))
        return records
