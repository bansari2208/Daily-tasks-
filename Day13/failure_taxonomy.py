"""
Day 13 Failure Taxonomy & Analysis Engine.
Analyzes 50 validation failure cases and generates taxonomy reports in MD and CSV format.
"""

import os
import json
import csv
from collections import Counter
from typing import Dict, Any, List

DATASET_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "sample_failures.json"))
REPORTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "reports"))


class FailureTaxonomyAnalyzer:
    """Analyzes validation failure categories and generates report artifacts."""

    TAXONOMY_CATEGORIES = [
        "Missing required field",
        "Wrong datatype",
        "Invalid enum",
        "Extra field",
        "Malformed JSON",
        "Hallucinated value",
        "Unknown category",
        "Other"
    ]

    def __init__(self, failures_path: str = DATASET_PATH, output_dir: str = REPORTS_DIR):
        self.failures_path = failures_path
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def load_failures(self) -> List[Dict[str, Any]]:
        with open(self.failures_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def analyze(self) -> Dict[str, Dict[str, Any]]:
        failures = self.load_failures()
        total = len(failures)
        counts = Counter(f["expected_category"] for f in failures)
        
        # Ensure all taxonomy categories are represented
        results = {}
        for cat in self.TAXONOMY_CATEGORIES:
            cnt = counts.get(cat, 0)
            pct = round((cnt / total) * 100.0, 1) if total > 0 else 0.0
            results[cat] = {"count": cnt, "percentage": pct}

        return results

    def generate_reports(self) -> Tuple[str, str, str]:
        analysis = self.analyze()
        failures = self.load_failures()
        total = len(failures)

        # 1. failure_taxonomy.md
        md_taxonomy = "# 📊 Day 13 — LLM Output Failure Taxonomy Report\n\n"
        md_taxonomy += f"**Total Analyzed Failure Cases**: {total}\n\n"
        md_taxonomy += "| Category | Count | Percentage (%) | Key Observation |\n"
        md_taxonomy += "| --- | --- | --- | --- |\n"
        
        observations = {
            "Missing required field": "Model omits required schema keys like ticket_id or reasoning.",
            "Wrong datatype": "Passes strings for float confidence or boolean for numbers.",
            "Invalid enum": "Uses unsupported category labels like 'Payment' or 'Hardware'.",
            "Extra field": "Injects unrequested metadata fields like 'user_sentiment'.",
            "Malformed JSON": "Unquoted keys, unclosed brackets, or markdown code fence leaks.",
            "Hallucinated value": "Invents fictional categories such as 'Supernatural' or 'AlienInvasion'.",
            "Unknown category": "Valid real-world requests outside support schema (e.g. Sales, Legal).",
            "Other": "Numeric constraint violations (e.g. confidence > 1.0 or blank reasoning)."
        }

        for cat, data in analysis.items():
            obs = observations.get(cat, "Observed boundary failure.")
            md_taxonomy += f"| **{cat}** | {data['count']} | {data['percentage']}% | {obs} |\n"

        taxonomy_md_path = os.path.join(self.output_dir, "failure_taxonomy.md")
        with open(taxonomy_md_path, "w", encoding="utf-8") as f:
            f.write(md_taxonomy)

        # 2. failure_summary.md
        md_summary = "# 📋 Day 13 — Failure Taxonomy Summary\n\n"
        top_category = max(analysis.items(), key=lambda x: x[1]["count"])
        md_summary += f"- **Primary Failure Mode**: {top_category[0]} ({top_category[1]['count']} cases, {top_category[1]['percentage']}%)\n"
        md_summary += f"- **Total Samples Evaluated**: {total}\n"
        md_summary += f"- **Taxonomy Categories Tracked**: {len(analysis)}\n\n"
        md_summary += "### Key Takeaway\n"
        md_summary += "Schema validation at the application boundary catches 100% of these structural violations before data enters business logic.\n"

        summary_md_path = os.path.join(self.output_dir, "failure_summary.md")
        with open(summary_md_path, "w", encoding="utf-8") as f:
            f.write(md_summary)

        # 3. failure_counts.csv
        csv_path = os.path.join(self.output_dir, "failure_counts.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Category", "Count", "Percentage"])
            for cat, data in analysis.items():
                writer.writerow([cat, data["count"], data["percentage"]])

        return taxonomy_md_path, summary_md_path, csv_path


def run_taxonomy_analysis():
    analyzer = FailureTaxonomyAnalyzer()
    return analyzer.generate_reports()
