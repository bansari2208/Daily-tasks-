# 📊 Day 13 — LLM Output Failure Taxonomy Report

**Total Analyzed Failure Cases**: 50

| Category | Count | Percentage (%) | Key Observation |
| --- | --- | --- | --- |
| **Missing required field** | 6 | 12.0% | Model omits required schema keys like ticket_id or reasoning. |
| **Wrong datatype** | 7 | 14.0% | Passes strings for float confidence or boolean for numbers. |
| **Invalid enum** | 6 | 12.0% | Uses unsupported category labels like 'Payment' or 'Hardware'. |
| **Extra field** | 6 | 12.0% | Injects unrequested metadata fields like 'user_sentiment'. |
| **Malformed JSON** | 6 | 12.0% | Unquoted keys, unclosed brackets, or markdown code fence leaks. |
| **Hallucinated value** | 7 | 14.0% | Invents fictional categories such as 'Supernatural' or 'AlienInvasion'. |
| **Unknown category** | 6 | 12.0% | Valid real-world requests outside support schema (e.g. Sales, Legal). |
| **Other** | 6 | 12.0% | Numeric constraint violations (e.g. confidence > 1.0 or blank reasoning). |
