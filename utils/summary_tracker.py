from pathlib import Path
import json
from typing import Dict

SUMMARY_FILE = Path("logs/summary.json")


def create_summary() -> Dict:
    """Initializes a blank summary dictionary structure."""
    return {
        "processed": [],
        "skipped": [],
        "total_scanned": 0
    }


def update_summary(summary: Dict, category: str, subject: str) -> None:
    """
    Updates the summary object with processed/skipped email info.

    Args:
        summary (Dict): Summary object tracking scanned emails.
        category (str): Either 'processed' or 'skipped'.
        subject (str): Email subject line.
    """
    if category not in summary:
        summary[category] = []
    summary[category].append(subject)
    summary["total_scanned"] += 1


def save_summary(summary: Dict) -> None:
    """
    Saves the summary data to a JSON file.

    Args:
        summary (Dict): Summary object to save.
    """
    SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SUMMARY_FILE, "w") as f:
        json.dump(summary, f, indent=4)
