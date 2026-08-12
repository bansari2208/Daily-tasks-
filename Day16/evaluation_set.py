"""
Day 16: Evaluation Set (30 Expense Claims)

Ground truth evaluation dataset containing 30 claims.
Includes the 8 mandatory hard cases and 22 additional test cases.
Each claim contains standardized fields for claim_id, expected_verdict, expected_breaches,
hard_case flag, and hard_case_type.
"""

EVALUATION_SET = [
    # ----------------------------------------------------
    # MANDATORY HARD CASES (Claims 1 - 8)
    # ----------------------------------------------------
    {
        "claim_id": "claim_001",
        "id": "claim_001",
        "name": "Hard Case 1: Line items do not add up to stated total",
        "submission_date": "2026-08-01",
        "claimant": "Alice Smith",
        "stated_total": 5000.0,
        "raw_text": "Claimant: Alice Smith\nSubmission Date: 2026-08-01\nStated Total: 5000.0 USD\nLine Items:\n1. 2026-07-25 | Services | Bistro Services | 2500.0 USD | Receipt: REC-101\n2. 2026-07-26 | Services | Tech Repair | 2000.0 USD | Receipt: REC-102",
        "input": "Claimant: Alice Smith\nSubmission Date: 2026-08-01\nStated Total: 5000.0 USD\nLine Items:\n1. 2026-07-25 | Services | Bistro Services | 2500.0 USD | Receipt: REC-101\n2. 2026-07-26 | Services | Tech Repair | 2000.0 USD | Receipt: REC-102",
        "line_items": [
            {"date": "2026-07-25", "category": "Services", "vendor": "Bistro Services", "amount": 2500.0, "receipt_ref": "REC-101"},
            {"date": "2026-07-26", "category": "Services", "vendor": "Tech Repair", "amount": 2000.0, "receipt_ref": "REC-102"}
        ],
        "hard_case": True,
        "hard_case_type": "arithmetic_discrepancy",
        "expected_verdict": "REVIEW",
        "expected_breaches": ["arithmetic_discrepancy"],
        "expected": {
            "verdict": "REVIEW",
            "breaches": ["arithmetic_discrepancy"]
        }
    },
    {
        "claim_id": "claim_002",
        "id": "claim_002",
        "name": "Hard Case 2: Meal claim slightly above daily cap",
        "submission_date": "2026-08-01",
        "claimant": "Bob Jones",
        "stated_total": 1250.0,
        "raw_text": "Claimant: Bob Jones\nSubmission Date: 2026-08-01\nStated Total: 1250.0 USD\nLine Items:\n1. 2026-07-28 | Meals | Gourmet Steakhouse | 1250.0 USD | Receipt: REC-201",
        "input": "Claimant: Bob Jones\nSubmission Date: 2026-08-01\nStated Total: 1250.0 USD\nLine Items:\n1. 2026-07-28 | Meals | Gourmet Steakhouse | 1250.0 USD | Receipt: REC-201",
        "line_items": [
            {"date": "2026-07-28", "category": "Meals", "vendor": "Gourmet Steakhouse", "amount": 1250.0, "receipt_ref": "REC-201"}
        ],
        "hard_case": True,
        "hard_case_type": "meal_daily_limit",
        "expected_verdict": "REVIEW",
        "expected_breaches": ["meal_daily_limit"],
        "expected": {
            "verdict": "REVIEW",
            "breaches": ["meal_daily_limit"]
        }
    },
    {
        "claim_id": "claim_003",
        "id": "claim_003",
        "name": "Hard Case 3: Claim breaching two rules at once",
        "submission_date": "2026-08-01",
        "claimant": "Charlie Brown",
        "stated_total": 8350.0,
        "raw_text": "Claimant: Charlie Brown\nSubmission Date: 2026-08-01\nStated Total: 8350.0 USD\nLine Items:\n1. 2026-07-20 | Meals | Luxury Dining | 1350.0 USD | Receipt: REC-301\n2. 2026-07-22 | Equipment | High-End Monitor | 7000.0 USD | Receipt: None",
        "input": "Claimant: Charlie Brown\nSubmission Date: 2026-08-01\nStated Total: 8350.0 USD\nLine Items:\n1. 2026-07-20 | Meals | Luxury Dining | 1350.0 USD | Receipt: REC-301\n2. 2026-07-22 | Equipment | High-End Monitor | 7000.0 USD | Receipt: None",
        "line_items": [
            {"date": "2026-07-20", "category": "Meals", "vendor": "Luxury Dining", "amount": 1350.0, "receipt_ref": "REC-301"},
            {"date": "2026-07-22", "category": "Equipment", "vendor": "High-End Monitor", "amount": 7000.0, "receipt_ref": None}
        ],
        "hard_case": True,
        "hard_case_type": "double_breach",
        "expected_verdict": "REJECT",
        "expected_breaches": ["meal_daily_limit", "missing_receipt"],
        "expected": {
            "verdict": "REJECT",
            "breaches": ["meal_daily_limit", "missing_receipt"]
        }
    },
    {
        "claim_id": "claim_004",
        "id": "claim_004",
        "name": "Hard Case 4: Expense dated 31 days before submission",
        "submission_date": "2026-08-01",
        "claimant": "Diana Prince",
        "stated_total": 800.0,
        "raw_text": "Claimant: Diana Prince\nSubmission Date: 2026-08-01\nStated Total: 800.0 USD\nLine Items:\n1. 2026-07-01 | Meals | Airport Cafe | 800.0 USD | Receipt: REC-401",
        "input": "Claimant: Diana Prince\nSubmission Date: 2026-08-01\nStated Total: 800.0 USD\nLine Items:\n1. 2026-07-01 | Meals | Airport Cafe | 800.0 USD | Receipt: REC-401",
        "line_items": [
            {"date": "2026-07-01", "category": "Meals", "vendor": "Airport Cafe", "amount": 800.0, "receipt_ref": "REC-401"}
        ],
        "hard_case": True,
        "hard_case_type": "expense_date_expired",
        "expected_verdict": "REJECT",
        "expected_breaches": ["expense_date_expired"],
        "expected": {
            "verdict": "REJECT",
            "breaches": ["expense_date_expired"]
        }
    },
    {
        "claim_id": "claim_005",
        "id": "claim_005",
        "name": "Hard Case 5: Item above 5,000 with no receipt reference",
        "submission_date": "2026-08-01",
        "claimant": "Evan Wright",
        "stated_total": 6500.0,
        "raw_text": "Claimant: Evan Wright\nSubmission Date: 2026-08-01\nStated Total: 6500.0 USD\nLine Items:\n1. 2026-07-25 | Equipment | Workstation Laptop | 6500.0 USD | Receipt: None",
        "input": "Claimant: Evan Wright\nSubmission Date: 2026-08-01\nStated Total: 6500.0 USD\nLine Items:\n1. 2026-07-25 | Equipment | Workstation Laptop | 6500.0 USD | Receipt: None",
        "line_items": [
            {"date": "2026-07-25", "category": "Equipment", "vendor": "Workstation Laptop", "amount": 6500.0, "receipt_ref": None}
        ],
        "hard_case": True,
        "hard_case_type": "missing_receipt",
        "expected_verdict": "REJECT",
        "expected_breaches": ["missing_receipt"],
        "expected": {
            "verdict": "REJECT",
            "breaches": ["missing_receipt"]
        }
    },
    {
        "claim_id": "claim_006",
        "id": "claim_006",
        "name": "Hard Case 6: Claim mixing two currencies",
        "submission_date": "2026-08-01",
        "claimant": "Fiona Gallagher",
        "stated_total": 650.0,
        "raw_text": "Claimant: Fiona Gallagher\nSubmission Date: 2026-08-01\nStated Total: 650.0 USD\nLine Items:\n1. 2026-07-20 | Travel | City Taxi | 150.0 USD | Receipt: REC-601\n2. 2026-07-21 | Meals | Euro Bistro | 500.0 EUR | Receipt: REC-602",
        "input": "Claimant: Fiona Gallagher\nSubmission Date: 2026-08-01\nStated Total: 650.0 USD\nLine Items:\n1. 2026-07-20 | Travel | City Taxi | 150.0 USD | Receipt: REC-601\n2. 2026-07-21 | Meals | Euro Bistro | 500.0 EUR | Receipt: REC-602",
        "line_items": [
            {"date": "2026-07-20", "category": "Travel", "vendor": "City Taxi", "amount": 150.0, "receipt_ref": "REC-601", "currency": "USD"},
            {"date": "2026-07-21", "category": "Meals", "vendor": "Euro Bistro", "amount": 500.0, "receipt_ref": "REC-602", "currency": "EUR"}
        ],
        "hard_case": True,
        "hard_case_type": "mixed_currencies",
        "expected_verdict": "REJECT",
        "expected_breaches": ["mixed_currencies"],
        "expected": {
            "verdict": "REJECT",
            "breaches": ["mixed_currencies"]
        }
    },
    {
        "claim_id": "claim_007",
        "id": "claim_007",
        "name": "Hard Case 7: Claim under total cap containing business-class travel",
        "submission_date": "2026-08-01",
        "claimant": "George Clark",
        "stated_total": 12000.0,
        "raw_text": "Claimant: George Clark\nSubmission Date: 2026-08-01\nStated Total: 12000.0 USD\nLine Items:\n1. 2026-07-15 | Travel | Sky Airways Business Class | 12000.0 USD | Receipt: REC-701",
        "input": "Claimant: George Clark\nSubmission Date: 2026-08-01\nStated Total: 12000.0 USD\nLine Items:\n1. 2026-07-15 | Travel | Sky Airways Business Class | 12000.0 USD | Receipt: REC-701",
        "line_items": [
            {"date": "2026-07-15", "category": "Travel", "vendor": "Sky Airways Business Class", "amount": 12000.0, "receipt_ref": "REC-701", "travel_class": "Business"}
        ],
        "hard_case": True,
        "hard_case_type": "travel_class_invalid",
        "expected_verdict": "REJECT",
        "expected_breaches": ["travel_class_invalid"],
        "expected": {
            "verdict": "REJECT",
            "breaches": ["travel_class_invalid"]
        }
    },
    {
        "claim_id": "claim_008",
        "id": "claim_008",
        "name": "Hard Case 8: One completely clean claim that must pass",
        "submission_date": "2026-08-01",
        "claimant": "Hannah Abbott",
        "stated_total": 1300.0,
        "raw_text": "Claimant: Hannah Abbott\nSubmission Date: 2026-08-01\nStated Total: 1300.0 USD\nLine Items:\n1. 2026-07-25 | Meals | Team Lunch | 900.0 USD | Receipt: REC-801\n2. 2026-07-26 | Travel | Metro Transit | 400.0 USD | Receipt: REC-802",
        "input": "Claimant: Hannah Abbott\nSubmission Date: 2026-08-01\nStated Total: 1300.0 USD\nLine Items:\n1. 2026-07-25 | Meals | Team Lunch | 900.0 USD | Receipt: REC-801\n2. 2026-07-26 | Travel | Metro Transit | 400.0 USD | Receipt: REC-802",
        "line_items": [
            {"date": "2026-07-25", "category": "Meals", "vendor": "Team Lunch", "amount": 900.0, "receipt_ref": "REC-801"},
            {"date": "2026-07-26", "category": "Travel", "vendor": "Metro Transit", "amount": 400.0, "receipt_ref": "REC-802"}
        ],
        "hard_case": True,
        "hard_case_type": "clean_claim_pass",
        "expected_verdict": "APPROVE",
        "expected_breaches": [],
        "expected": {
            "verdict": "APPROVE",
            "breaches": []
        }
    },

    # ----------------------------------------------------
    # REMAINING CLAIMS (Claims 9 - 30)
    # ----------------------------------------------------
    {
        "claim_id": "claim_009",
        "id": "claim_009",
        "name": "Clean Travel Economy Claim",
        "submission_date": "2026-08-01",
        "claimant": "Ian Malcolm",
        "stated_total": 14000.0,
        "raw_text": "Claimant: Ian Malcolm\nSubmission Date: 2026-08-01\nStated Total: 14000.0 USD\nLine Items:\n1. 2026-07-20 | Travel | Global Airlines Economy Flight | 14000.0 USD | Receipt: REC-901",
        "input": "Claimant: Ian Malcolm\nSubmission Date: 2026-08-01\nStated Total: 14000.0 USD\nLine Items:\n1. 2026-07-20 | Travel | Global Airlines Economy Flight | 14000.0 USD | Receipt: REC-901",
        "line_items": [
            {"date": "2026-07-20", "category": "Travel", "vendor": "Global Airlines Economy Flight", "amount": 14000.0, "receipt_ref": "REC-901", "travel_class": "Economy"}
        ],
        "hard_case": False,
        "hard_case_type": None,
        "expected_verdict": "APPROVE",
        "expected_breaches": [],
        "expected": {
            "verdict": "APPROVE",
            "breaches": []
        }
    },
    {
        "claim_id": "claim_010",
        "id": "claim_010",
        "name": "Travel limit exceeded (>15,000 per trip)",
        "submission_date": "2026-08-01",
        "claimant": "Julia Roberts",
        "stated_total": 18000.0,
        "raw_text": "Claimant: Julia Roberts\nSubmission Date: 2026-08-01\nStated Total: 18000.0 USD\nLine Items:\n1. 2026-07-15 | Travel | Transatlantic Flight Economy | 18000.0 USD | Receipt: REC-1001",
        "input": "Claimant: Julia Roberts\nSubmission Date: 2026-08-01\nStated Total: 18000.0 USD\nLine Items:\n1. 2026-07-15 | Travel | Transatlantic Flight Economy | 18000.0 USD | Receipt: REC-1001",
        "line_items": [
            {"date": "2026-07-15", "category": "Travel", "vendor": "Transatlantic Flight Economy", "amount": 18000.0, "receipt_ref": "REC-1001"}
        ],
        "hard_case": False,
        "hard_case_type": None,
        "expected_verdict": "REJECT",
        "expected_breaches": ["travel_limit_exceeded"],
        "expected": {
            "verdict": "REJECT",
            "breaches": ["travel_limit_exceeded"]
        }
    },
    {
        "claim_id": "claim_011",
        "id": "claim_011",
        "name": "Total claim exceeds 50,000 cap",
        "submission_date": "2026-08-01",
        "claimant": "Kevin Spacey",
        "stated_total": 55000.0,
        "raw_text": "Claimant: Kevin Spacey\nSubmission Date: 2026-08-01\nStated Total: 55000.0 USD\nLine Items:\n1. 2026-07-10 | Equipment | Server Rack Cluster | 55000.0 USD | Receipt: REC-1101",
        "input": "Claimant: Kevin Spacey\nSubmission Date: 2026-08-01\nStated Total: 55000.0 USD\nLine Items:\n1. 2026-07-10 | Equipment | Server Rack Cluster | 55000.0 USD | Receipt: REC-1101",
        "line_items": [
            {"date": "2026-07-10", "category": "Equipment", "vendor": "Server Rack Cluster", "amount": 55000.0, "receipt_ref": "REC-1101"}
        ],
        "hard_case": False,
        "hard_case_type": None,
        "expected_verdict": "REJECT",
        "expected_breaches": ["total_claim_cap_exceeded"],
        "expected": {
            "verdict": "REJECT",
            "breaches": ["total_claim_cap_exceeded"]
        }
    },
    {
        "claim_id": "claim_012",
        "id": "claim_012",
        "name": "Clean Software Subscription Claim",
        "submission_date": "2026-08-01",
        "claimant": "Laura Croft",
        "stated_total": 3000.0,
        "raw_text": "Claimant: Laura Croft\nSubmission Date: 2026-08-01\nStated Total: 3000.0 USD\nLine Items:\n1. 2026-07-22 | Services | Cloud Hosting Subscription | 3000.0 USD | Receipt: REC-1201",
        "input": "Claimant: Laura Croft\nSubmission Date: 2026-08-01\nStated Total: 3000.0 USD\nLine Items:\n1. 2026-07-22 | Services | Cloud Hosting Subscription | 3000.0 USD | Receipt: REC-1201",
        "line_items": [
            {"date": "2026-07-22", "category": "Services", "vendor": "Cloud Hosting Subscription", "amount": 3000.0, "receipt_ref": "REC-1201"}
        ],
        "hard_case": False,
        "hard_case_type": None,
        "expected_verdict": "APPROVE",
        "expected_breaches": [],
        "expected": {
            "verdict": "APPROVE",
            "breaches": []
        }
    },
    {
        "claim_id": "claim_013",
        "id": "claim_013",
        "name": "Missing receipt for item over 5,000",
        "submission_date": "2026-08-01",
        "claimant": "Michael Scott",
        "stated_total": 5500.0,
        "raw_text": "Claimant: Michael Scott\nSubmission Date: 2026-08-01\nStated Total: 5500.0 USD\nLine Items:\n1. 2026-07-20 | Services | Consulting Fee | 5500.0 USD | Receipt: None",
        "input": "Claimant: Michael Scott\nSubmission Date: 2026-08-01\nStated Total: 5500.0 USD\nLine Items:\n1. 2026-07-20 | Services | Consulting Fee | 5500.0 USD | Receipt: None",
        "line_items": [
            {"date": "2026-07-20", "category": "Services", "vendor": "Consulting Fee", "amount": 5500.0, "receipt_ref": None}
        ],
        "hard_case": False,
        "hard_case_type": None,
        "expected_verdict": "REJECT",
        "expected_breaches": ["missing_receipt"],
        "expected": {
            "verdict": "REJECT",
            "breaches": ["missing_receipt"]
        }
    },
    {
        "claim_id": "claim_014",
        "id": "claim_014",
        "name": "Expense 45 days old",
        "submission_date": "2026-08-01",
        "claimant": "Nancy Wheeler",
        "stated_total": 1200.0,
        "raw_text": "Claimant: Nancy Wheeler\nSubmission Date: 2026-08-01\nStated Total: 1200.0 USD\nLine Items:\n1. 2026-06-15 | Equipment | Office Desk Chair | 1200.0 USD | Receipt: REC-1401",
        "input": "Claimant: Nancy Wheeler\nSubmission Date: 2026-08-01\nStated Total: 1200.0 USD\nLine Items:\n1. 2026-06-15 | Equipment | Office Desk Chair | 1200.0 USD | Receipt: REC-1401",
        "line_items": [
            {"date": "2026-06-15", "category": "Equipment", "vendor": "Office Desk Chair", "amount": 1200.0, "receipt_ref": "REC-1401"}
        ],
        "hard_case": False,
        "hard_case_type": None,
        "expected_verdict": "REJECT",
        "expected_breaches": ["expense_date_expired"],
        "expected": {
            "verdict": "REJECT",
            "breaches": ["expense_date_expired"]
        }
    },
    {
        "claim_id": "claim_015",
        "id": "claim_015",
        "name": "Clean Multi-item Meals & Travel Claim",
        "submission_date": "2026-08-01",
        "claimant": "Oscar Martinez",
        "stated_total": 1400.0,
        "raw_text": "Claimant: Oscar Martinez\nSubmission Date: 2026-08-01\nStated Total: 1400.0 USD\nLine Items:\n1. 2026-07-29 | Meals | Executive Diner | 1100.0 USD | Receipt: REC-1501\n2. 2026-07-30 | Travel | City Cab | 300.0 USD | Receipt: REC-1502",
        "input": "Claimant: Oscar Martinez\nSubmission Date: 2026-08-01\nStated Total: 1400.0 USD\nLine Items:\n1. 2026-07-29 | Meals | Executive Diner | 1100.0 USD | Receipt: REC-1501\n2. 2026-07-30 | Travel | City Cab | 300.0 USD | Receipt: REC-1502",
        "line_items": [
            {"date": "2026-07-29", "category": "Meals", "vendor": "Executive Diner", "amount": 1100.0, "receipt_ref": "REC-1501"},
            {"date": "2026-07-30", "category": "Travel", "vendor": "City Cab", "amount": 300.0, "receipt_ref": "REC-1502"}
        ],
        "hard_case": False,
        "hard_case_type": None,
        "expected_verdict": "APPROVE",
        "expected_breaches": [],
        "expected": {
            "verdict": "APPROVE",
            "breaches": []
        }
    },
    {
        "claim_id": "claim_016",
        "id": "claim_016",
        "name": "Meal daily cap exceeded (1,500 on single day)",
        "submission_date": "2026-08-01",
        "claimant": "Pam Beesly",
        "stated_total": 1500.0,
        "raw_text": "Claimant: Pam Beesly\nSubmission Date: 2026-08-01\nStated Total: 1500.0 USD\nLine Items:\n1. 2026-07-27 | Meals | Italian Trattoria | 1500.0 USD | Receipt: REC-1601",
        "input": "Claimant: Pam Beesly\nSubmission Date: 2026-08-01\nStated Total: 1500.0 USD\nLine Items:\n1. 2026-07-27 | Meals | Italian Trattoria | 1500.0 USD | Receipt: REC-1601",
        "line_items": [
            {"date": "2026-07-27", "category": "Meals", "vendor": "Italian Trattoria", "amount": 1500.0, "receipt_ref": "REC-1601"}
        ],
        "hard_case": False,
        "hard_case_type": None,
        "expected_verdict": "REVIEW",
        "expected_breaches": ["meal_daily_limit"],
        "expected": {
            "verdict": "REVIEW",
            "breaches": ["meal_daily_limit"]
        }
    },
    {
        "claim_id": "claim_017",
        "id": "claim_017",
        "name": "Arithmetic mismatch (stated 3500, sum 3000)",
        "submission_date": "2026-08-01",
        "claimant": "Quentin Tarantino",
        "stated_total": 3500.0,
        "raw_text": "Claimant: Quentin Tarantino\nSubmission Date: 2026-08-01\nStated Total: 3500.0 USD\nLine Items:\n1. 2026-07-20 | Services | Editing Software | 1500.0 USD | Receipt: REC-1701\n2. 2026-07-21 | Equipment | Microphones | 1500.0 USD | Receipt: REC-1702",
        "input": "Claimant: Quentin Tarantino\nSubmission Date: 2026-08-01\nStated Total: 3500.0 USD\nLine Items:\n1. 2026-07-20 | Services | Editing Software | 1500.0 USD | Receipt: REC-1701\n2. 2026-07-21 | Equipment | Microphones | 1500.0 USD | Receipt: REC-1702",
        "line_items": [
            {"date": "2026-07-20", "category": "Services", "vendor": "Editing Software", "amount": 1500.0, "receipt_ref": "REC-1701"},
            {"date": "2026-07-21", "category": "Equipment", "vendor": "Microphones", "amount": 1500.0, "receipt_ref": "REC-1702"}
        ],
        "hard_case": False,
        "hard_case_type": None,
        "expected_verdict": "REVIEW",
        "expected_breaches": ["arithmetic_discrepancy"],
        "expected": {
            "verdict": "REVIEW",
            "breaches": ["arithmetic_discrepancy"]
        }
    },
    {
        "claim_id": "claim_018",
        "id": "claim_018",
        "name": "Clean Office Supplies Claim",
        "submission_date": "2026-08-01",
        "claimant": "Rachel Green",
        "stated_total": 4500.0,
        "raw_text": "Claimant: Rachel Green\nSubmission Date: 2026-08-01\nStated Total: 4500.0 USD\nLine Items:\n1. 2026-07-26 | Equipment | Ergonomic Chairs | 4500.0 USD | Receipt: REC-1801",
        "input": "Claimant: Rachel Green\nSubmission Date: 2026-08-01\nStated Total: 4500.0 USD\nLine Items:\n1. 2026-07-26 | Equipment | Ergonomic Chairs | 4500.0 USD | Receipt: REC-1801",
        "line_items": [
            {"date": "2026-07-26", "category": "Equipment", "vendor": "Ergonomic Chairs", "amount": 4500.0, "receipt_ref": "REC-1801"}
        ],
        "hard_case": False,
        "hard_case_type": None,
        "expected_verdict": "APPROVE",
        "expected_breaches": [],
        "expected": {
            "verdict": "APPROVE",
            "breaches": []
        }
    },
    {
        "claim_id": "claim_019",
        "id": "claim_019",
        "name": "Travel Non-Economy (First Class)",
        "submission_date": "2026-08-01",
        "claimant": "Steve Rogers",
        "stated_total": 9000.0,
        "raw_text": "Claimant: Steve Rogers\nSubmission Date: 2026-08-01\nStated Total: 9000.0 USD\nLine Items:\n1. 2026-07-18 | Travel | Pacific Air First Class | 9000.0 USD | Receipt: REC-1901",
        "input": "Claimant: Steve Rogers\nSubmission Date: 2026-08-01\nStated Total: 9000.0 USD\nLine Items:\n1. 2026-07-18 | Travel | Pacific Air First Class | 9000.0 USD | Receipt: REC-1901",
        "line_items": [
            {"date": "2026-07-18", "category": "Travel", "vendor": "Pacific Air First Class", "amount": 9000.0, "receipt_ref": "REC-1901", "travel_class": "First Class"}
        ],
        "hard_case": False,
        "hard_case_type": None,
        "expected_verdict": "REJECT",
        "expected_breaches": ["travel_class_invalid"],
        "expected": {
            "verdict": "REJECT",
            "breaches": ["travel_class_invalid"]
        }
    },
    {
        "claim_id": "claim_020",
        "id": "claim_020",
        "name": "Double Breach: Claim cap >50k and expense 40 days old",
        "submission_date": "2026-08-01",
        "claimant": "Tony Stark",
        "stated_total": 52000.0,
        "raw_text": "Claimant: Tony Stark\nSubmission Date: 2026-08-01\nStated Total: 52000.0 USD\nLine Items:\n1. 2026-06-20 | Equipment | Quantum Processor | 52000.0 USD | Receipt: REC-2001",
        "input": "Claimant: Tony Stark\nSubmission Date: 2026-08-01\nStated Total: 52000.0 USD\nLine Items:\n1. 2026-06-20 | Equipment | Quantum Processor | 52000.0 USD | Receipt: REC-2001",
        "line_items": [
            {"date": "2026-06-20", "category": "Equipment", "vendor": "Quantum Processor", "amount": 52000.0, "receipt_ref": "REC-2001"}
        ],
        "hard_case": False,
        "hard_case_type": None,
        "expected_verdict": "REJECT",
        "expected_breaches": ["total_claim_cap_exceeded", "expense_date_expired"],
        "expected": {
            "verdict": "REJECT",
            "breaches": ["total_claim_cap_exceeded", "expense_date_expired"]
        }
    },
    {
        "claim_id": "claim_021",
        "id": "claim_021",
        "name": "Clean Client Dinner Claim",
        "submission_date": "2026-08-01",
        "claimant": "Ursula Buffay",
        "stated_total": 1150.0,
        "raw_text": "Claimant: Ursula Buffay\nSubmission Date: 2026-08-01\nStated Total: 1150.0 USD\nLine Items:\n1. 2026-07-29 | Meals | Seafood Restaurant | 1150.0 USD | Receipt: REC-2101",
        "input": "Claimant: Ursula Buffay\nSubmission Date: 2026-08-01\nStated Total: 1150.0 USD\nLine Items:\n1. 2026-07-29 | Meals | Seafood Restaurant | 1150.0 USD | Receipt: REC-2101",
        "line_items": [
            {"date": "2026-07-29", "category": "Meals", "vendor": "Seafood Restaurant", "amount": 1150.0, "receipt_ref": "REC-2101"}
        ],
        "hard_case": False,
        "hard_case_type": None,
        "expected_verdict": "APPROVE",
        "expected_breaches": [],
        "expected": {
            "verdict": "APPROVE",
            "breaches": []
        }
    },
    {
        "claim_id": "claim_022",
        "id": "claim_022",
        "name": "Meal cap exceeded (1,400 on single day)",
        "submission_date": "2026-08-01",
        "claimant": "Victor Stone",
        "stated_total": 1400.0,
        "raw_text": "Claimant: Victor Stone\nSubmission Date: 2026-08-01\nStated Total: 1400.0 USD\nLine Items:\n1. 2026-07-27 | Meals | Downtown Grill | 1400.0 USD | Receipt: REC-2201",
        "input": "Claimant: Victor Stone\nSubmission Date: 2026-08-01\nStated Total: 1400.0 USD\nLine Items:\n1. 2026-07-27 | Meals | Downtown Grill | 1400.0 USD | Receipt: REC-2201",
        "line_items": [
            {"date": "2026-07-27", "category": "Meals", "vendor": "Downtown Grill", "amount": 1400.0, "receipt_ref": "REC-2201"}
        ],
        "hard_case": False,
        "hard_case_type": None,
        "expected_verdict": "REVIEW",
        "expected_breaches": ["meal_daily_limit"],
        "expected": {
            "verdict": "REVIEW",
            "breaches": ["meal_daily_limit"]
        }
    },
    {
        "claim_id": "claim_023",
        "id": "claim_023",
        "name": "Item 8,000 missing receipt",
        "submission_date": "2026-08-01",
        "claimant": "Wanda Maximoff",
        "stated_total": 8000.0,
        "raw_text": "Claimant: Wanda Maximoff\nSubmission Date: 2026-08-01\nStated Total: 8000.0 USD\nLine Items:\n1. 2026-07-24 | Services | Security Audit | 8000.0 USD | Receipt: None",
        "input": "Claimant: Wanda Maximoff\nSubmission Date: 2026-08-01\nStated Total: 8000.0 USD\nLine Items:\n1. 2026-07-24 | Services | Security Audit | 8000.0 USD | Receipt: None",
        "line_items": [
            {"date": "2026-07-24", "category": "Services", "vendor": "Security Audit", "amount": 8000.0, "receipt_ref": None}
        ],
        "hard_case": False,
        "hard_case_type": None,
        "expected_verdict": "REJECT",
        "expected_breaches": ["missing_receipt"],
        "expected": {
            "verdict": "REJECT",
            "breaches": ["missing_receipt"]
        }
    },
    {
        "claim_id": "claim_024",
        "id": "claim_024",
        "name": "Clean Hotel Accommodations Claim with valid receipt",
        "submission_date": "2026-08-01",
        "claimant": "Xavier Charles",
        "stated_total": 8000.0,
        "raw_text": "Claimant: Xavier Charles\nSubmission Date: 2026-08-01\nStated Total: 8000.0 USD\nLine Items:\n1. 2026-07-21 | Travel | Grand Plaza Hotel | 8000.0 USD | Receipt: REC-2401",
        "input": "Claimant: Xavier Charles\nSubmission Date: 2026-08-01\nStated Total: 8000.0 USD\nLine Items:\n1. 2026-07-21 | Travel | Grand Plaza Hotel | 8000.0 USD | Receipt: REC-2401",
        "line_items": [
            {"date": "2026-07-21", "category": "Travel", "vendor": "Grand Plaza Hotel", "amount": 8000.0, "receipt_ref": "REC-2401"}
        ],
        "hard_case": False,
        "hard_case_type": None,
        "expected_verdict": "APPROVE",
        "expected_breaches": [],
        "expected": {
            "verdict": "APPROVE",
            "breaches": []
        }
    },
    {
        "claim_id": "claim_025",
        "id": "claim_025",
        "name": "Expense 35 days old",
        "submission_date": "2026-08-01",
        "claimant": "Yelena Belova",
        "stated_total": 2100.0,
        "raw_text": "Claimant: Yelena Belova\nSubmission Date: 2026-08-01\nStated Total: 2100.0 USD\nLine Items:\n1. 2026-06-27 | Services | Training Course | 2100.0 USD | Receipt: REC-2501",
        "input": "Claimant: Yelena Belova\nSubmission Date: 2026-08-01\nStated Total: 2100.0 USD\nLine Items:\n1. 2026-06-27 | Services | Training Course | 2100.0 USD | Receipt: REC-2501",
        "line_items": [
            {"date": "2026-06-27", "category": "Services", "vendor": "Training Course", "amount": 2100.0, "receipt_ref": "REC-2501"}
        ],
        "hard_case": False,
        "hard_case_type": None,
        "expected_verdict": "REJECT",
        "expected_breaches": ["expense_date_expired"],
        "expected": {
            "verdict": "REJECT",
            "breaches": ["expense_date_expired"]
        }
    },
    {
        "claim_id": "claim_026",
        "id": "claim_026",
        "name": "Mixed currencies (USD and GBP)",
        "submission_date": "2026-08-01",
        "claimant": "Zack Snyder",
        "stated_total": 1200.0,
        "raw_text": "Claimant: Zack Snyder\nSubmission Date: 2026-08-01\nStated Total: 1200.0 USD\nLine Items:\n1. 2026-07-20 | Meals | London Pub | 700.0 GBP | Receipt: REC-2601\n2. 2026-07-21 | Travel | US Transit | 500.0 USD | Receipt: REC-2602",
        "input": "Claimant: Zack Snyder\nSubmission Date: 2026-08-01\nStated Total: 1200.0 USD\nLine Items:\n1. 2026-07-20 | Meals | London Pub | 700.0 GBP | Receipt: REC-2601\n2. 2026-07-21 | Travel | US Transit | 500.0 USD | Receipt: REC-2602",
        "line_items": [
            {"date": "2026-07-20", "category": "Meals", "vendor": "London Pub", "amount": 700.0, "receipt_ref": "REC-2601", "currency": "GBP"},
            {"date": "2026-07-21", "category": "Travel", "vendor": "US Transit", "amount": 500.0, "receipt_ref": "REC-2602", "currency": "USD"}
        ],
        "hard_case": False,
        "hard_case_type": None,
        "expected_verdict": "REJECT",
        "expected_breaches": ["mixed_currencies"],
        "expected": {
            "verdict": "REJECT",
            "breaches": ["mixed_currencies"]
        }
    },
    {
        "claim_id": "claim_027",
        "id": "claim_027",
        "name": "Clean Taxi and Lunch Claim",
        "submission_date": "2026-08-01",
        "claimant": "Arthur Pendelton",
        "stated_total": 1100.0,
        "raw_text": "Claimant: Arthur Pendelton\nSubmission Date: 2026-08-01\nStated Total: 1100.0 USD\nLine Items:\n1. 2026-07-28 | Travel | Metro Cab | 600.0 USD | Receipt: REC-2701\n2. 2026-07-28 | Meals | Corner Cafe | 500.0 USD | Receipt: REC-2702",
        "input": "Claimant: Arthur Pendelton\nSubmission Date: 2026-08-01\nStated Total: 1100.0 USD\nLine Items:\n1. 2026-07-28 | Travel | Metro Cab | 600.0 USD | Receipt: REC-2701\n2. 2026-07-28 | Meals | Corner Cafe | 500.0 USD | Receipt: REC-2702",
        "line_items": [
            {"date": "2026-07-28", "category": "Travel", "vendor": "Metro Cab", "amount": 600.0, "receipt_ref": "REC-2701"},
            {"date": "2026-07-28", "category": "Meals", "vendor": "Corner Cafe", "amount": 500.0, "receipt_ref": "REC-2702"}
        ],
        "hard_case": False,
        "hard_case_type": None,
        "expected_verdict": "APPROVE",
        "expected_breaches": [],
        "expected": {
            "verdict": "APPROVE",
            "breaches": []
        }
    },
    {
        "claim_id": "claim_028",
        "id": "claim_028",
        "name": "Arithmetic mismatch (stated 6500, sum 7000)",
        "submission_date": "2026-08-01",
        "claimant": "Bruce Wayne",
        "stated_total": 6500.0,
        "raw_text": "Claimant: Bruce Wayne\nSubmission Date: 2026-08-01\nStated Total: 6500.0 USD\nLine Items:\n1. 2026-07-25 | Equipment | Tech Gadgets | 4000.0 USD | Receipt: REC-2801\n2. 2026-07-26 | Services | Security Consultation | 3000.0 USD | Receipt: REC-2802",
        "input": "Claimant: Bruce Wayne\nSubmission Date: 2026-08-01\nStated Total: 6500.0 USD\nLine Items:\n1. 2026-07-25 | Equipment | Tech Gadgets | 4000.0 USD | Receipt: REC-2801\n2. 2026-07-26 | Services | Security Consultation | 3000.0 USD | Receipt: REC-2802",
        "line_items": [
            {"date": "2026-07-25", "category": "Equipment", "vendor": "Tech Gadgets", "amount": 4000.0, "receipt_ref": "REC-2801"},
            {"date": "2026-07-26", "category": "Services", "vendor": "Security Consultation", "amount": 3000.0, "receipt_ref": "REC-2802"}
        ],
        "hard_case": False,
        "hard_case_type": None,
        "expected_verdict": "REVIEW",
        "expected_breaches": ["arithmetic_discrepancy"],
        "expected": {
            "verdict": "REVIEW",
            "breaches": ["arithmetic_discrepancy"]
        }
    },
    {
        "claim_id": "claim_029",
        "id": "claim_029",
        "name": "Travel 16,000 exceeding 15k limit",
        "submission_date": "2026-08-01",
        "claimant": "Clark Kent",
        "stated_total": 16000.0,
        "raw_text": "Claimant: Clark Kent\nSubmission Date: 2026-08-01\nStated Total: 16000.0 USD\nLine Items:\n1. 2026-07-12 | Travel | International Flight Economy | 16000.0 USD | Receipt: REC-2901",
        "input": "Claimant: Clark Kent\nSubmission Date: 2026-08-01\nStated Total: 16000.0 USD\nLine Items:\n1. 2026-07-12 | Travel | International Flight Economy | 16000.0 USD | Receipt: REC-2901",
        "line_items": [
            {"date": "2026-07-12", "category": "Travel", "vendor": "International Flight Economy", "amount": 16000.0, "receipt_ref": "REC-2901"}
        ],
        "hard_case": False,
        "hard_case_type": None,
        "expected_verdict": "REJECT",
        "expected_breaches": ["travel_limit_exceeded"],
        "expected": {
            "verdict": "REJECT",
            "breaches": ["travel_limit_exceeded"]
        }
    },
    {
        "claim_id": "claim_030",
        "id": "claim_030",
        "name": "Clean Train & Hotel Claim",
        "submission_date": "2026-08-01",
        "claimant": "Diana Prince",
        "stated_total": 5200.0,
        "raw_text": "Claimant: Diana Prince\nSubmission Date: 2026-08-01\nStated Total: 5200.0 USD\nLine Items:\n1. 2026-07-22 | Travel | Express Train | 1200.0 USD | Receipt: REC-3001\n2. 2026-07-23 | Travel | City Center Hotel | 4000.0 USD | Receipt: REC-3002",
        "input": "Claimant: Diana Prince\nSubmission Date: 2026-08-01\nStated Total: 5200.0 USD\nLine Items:\n1. 2026-07-22 | Travel | Express Train | 1200.0 USD | Receipt: REC-3001\n2. 2026-07-23 | Travel | City Center Hotel | 4000.0 USD | Receipt: REC-3002",
        "line_items": [
            {"date": "2026-07-22", "category": "Travel", "vendor": "Express Train", "amount": 1200.0, "receipt_ref": "REC-3001"},
            {"date": "2026-07-23", "category": "Travel", "vendor": "City Center Hotel", "amount": 4000.0, "receipt_ref": "REC-3002"}
        ],
        "hard_case": False,
        "hard_case_type": None,
        "expected_verdict": "APPROVE",
        "expected_breaches": [],
    }
]


def validate_evaluation_dataset(claims=EVALUATION_SET) -> bool:
    """
    Task 4: Validates the ground-truth evaluation set.
    Verifies 30 claims, unique claim_ids, hard cases, required categories, and clean claim.
    Fails loudly with ValueError if any constraint is violated.
    """
    if len(claims) != 30:
        raise ValueError(f"Dataset validation failed: Expected exactly 30 claims, got {len(claims)}")

    claim_ids = [c.get("claim_id") or c.get("id") for c in claims]
    if len(claim_ids) != len(set(claim_ids)):
        duplicates = [cid for cid in claim_ids if claim_ids.count(cid) > 1]
        raise ValueError(f"Dataset validation failed: Duplicate claim_id values found: {set(duplicates)}")

    hard_cases = [c for c in claims if c.get("hard_case", False) is True]
    if len(hard_cases) < 8:
        raise ValueError(f"Dataset validation failed: Expected at least 8 hard cases, found {len(hard_cases)}")

    required_hard_types = {
        "arithmetic_discrepancy",
        "meal_daily_limit",
        "double_breach",
        "expense_date_expired",
        "missing_receipt",
        "mixed_currencies",
        "travel_class_invalid",
        "clean_claim_pass"
    }
    found_hard_types = set(c.get("hard_case_type") for c in hard_cases if c.get("hard_case_type"))
    missing_types = required_hard_types - found_hard_types
    if missing_types:
        raise ValueError(f"Dataset validation failed: Missing required hard-case categories: {missing_types}")

    has_clean_claim = any(c.get("expected_verdict") == "APPROVE" and len(c.get("expected_breaches", [])) == 0 for c in claims)
    if not has_clean_claim:
        raise ValueError("Dataset validation failed: Missing at least one clean passing claim (APPROVE with no breaches).")

    for c in claims:
        cid = c.get("claim_id") or c.get("id")
        if not c.get("expected_verdict"):
            raise ValueError(f"Dataset validation failed: Claim {cid} missing expected_verdict")
        if c.get("expected_breaches") is None:
            raise ValueError(f"Dataset validation failed: Claim {cid} missing expected_breaches")
        if "hard_case" not in c:
            raise ValueError(f"Dataset validation failed: Claim {cid} missing hard_case flag")

    return True


# Run validation on import to fail loudly if dataset is invalid
validate_evaluation_dataset()

