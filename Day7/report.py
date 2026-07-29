import sys
import os

# Ensure ticket_classifier package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ticket_classifier.report import generate_report

if __name__ == "__main__":
    generate_report()
