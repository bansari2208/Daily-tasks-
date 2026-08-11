"""
Day 16: Evaluation Set (30 Expense Claims)

Ground truth evaluation dataset containing 30 claims.
Includes the 8 mandatory hard cases and 22 additional test cases.
"""

EVALUATION_SET = [
    # ----------------------------------------------------
    # MANDATORY HARD CASES (Claims 1 - 8)
    # ----------------------------------------------------
    {
        "id": "claim_001",
        "name": "Hard Case 1: Line items do not add up to stated total",
        "submission_date": "2026-08-01",
        "claimant": "Alice Smith",
        "stated_total": 5000.0,
        "raw_text": "Claimant: Alice Smith\nSubmission Date: 2026-08-01\nStated Total: 5000.0 USD\nLine Items:\n1. 2026-07-25 | Meals | Bistro Diner | 2500.0 USD | Receipt: REC-101\n2. 2026-07-26 | Services | Tech Repair | 2000.0 USD | Receipt: REC-102",
        "line_items": [
            {"date": "2026-07-25", "category": "Meals", "vendor": "Bistro Diner", "amount": 2500.0, "receipt_ref": "REC-101"},
            {"date": "2026-07-26", "category": "Services", "vendor": "Tech Repair", "amount": 2000.0, "receipt_ref": "REC-102"}
        ],
        "expected": {
            "verdict": "REVIEW",
            "breaches": ["Arithmetic discrepancy: line items sum to 4500.0 but stated total is 5000.0"]
        }
    },
    {
        "id": "claim_002",
        "name": "Hard Case 2: Meal claim slightly above daily cap",
        "submission_date": "2026-08-01",
        "claimant": "Bob Jones",
        "stated_total": 1250.0,
        "raw_text": "Claimant: Bob Jones\nSubmission Date: 2026-08-01\nStated Total: 1250.0 USD\nLine Items:\n1. 2026-07-28 | Meals | Gourmet Steakhouse | 1250.0 USD | Receipt: REC-201",
        "line_items": [
            {"date": "2026-07-28", "category": "Meals", "vendor": "Gourmet Steakhouse", "amount": 1250.0, "receipt_ref": "REC-201"}
        ],
        "expected": {
            "verdict": "REVIEW",
            "breaches": ["Meal daily cap exceeded: 1250.0 on 2026-07-28 at Gourmet Steakhouse (max 1200/day)"]
        }
    },
    {
        "id": "claim_003",
        "name": "Hard Case 3: Claim breaching two rules at once",
        "submission_date": "2026-08-01",
        "claimant": "Charlie Brown",
        "stated_total": 8350.0,
        "raw_text": "Claimant: Charlie Brown\nSubmission Date: 2026-08-01\nStated Total: 8350.0 USD\nLine Items:\n1. 2026-07-20 | Meals | Luxury Dining | 1350.0 USD | Receipt: REC-301\n2. 2026-07-22 | Equipment | High-End Monitor | 7000.0 USD | Receipt: None",
        "line_items": [
            {"date": "2026-07-20", "category": "Meals", "vendor": "Luxury Dining", "amount": 1350.0, "receipt_ref": "REC-301"},
            {"date": "2026-07-22", "category": "Equipment", "vendor": "High-End Monitor", "amount": 7000.0, "receipt_ref": None}
        ],
        "expected": {
            "verdict": "REJECT",
            "breaches": [
                "Meal daily cap exceeded: 1350.0 at Luxury Dining (max 1200/day)",
                "Missing receipt reference for item over 5,000: High-End Monitor 7000.0"
            ]
        }
    },
    {
        "id": "claim_004",
        "name": "Hard Case 4: Expense dated 31 days before submission",
        "submission_date": "2026-08-01",
        "claimant": "Diana Prince",
        "stated_total": 800.0,
        "raw_text": "Claimant: Diana Prince\nSubmission Date: 2026-08-01\nStated Total: 800.0 USD\nLine Items:\n1. 2026-07-01 | Meals | Airport Cafe | 800.0 USD | Receipt: REC-401",
        "line_items": [
            {"date": "2026-07-01", "category": "Meals", "vendor": "Airport Cafe", "amount": 800.0, "receipt_ref": "REC-401"}
        ],
        "expected": {
            "verdict": "REJECT",
            "breaches": ["Expense date older than 30 days: 2026-07-01 submitted on 2026-08-01 (31 days)"]
        }
    },
    {
        "id": "claim_005",
        "name": "Hard Case 5: Item above 5,000 with no receipt reference",
        "submission_date": "2026-08-01",
        "claimant": "Evan Wright",
        "stated_total": 6500.0,
        "raw_text": "Claimant: Evan Wright\nSubmission Date: 2026-08-01\nStated Total: 6500.0 USD\nLine Items:\n1. 2026-07-25 | Equipment | Workstation Laptop | 6500.0 USD | Receipt: None",
        "line_items": [
            {"date": "2026-07-25", "category": "Equipment", "vendor": "Workstation Laptop", "amount": 6500.0, "receipt_ref": None}
        ],
        "expected": {
            "verdict": "REJECT",
            "breaches": ["Missing receipt reference for item over 5,000: Workstation Laptop 6500.0"]
        }
    },
    {
        "id": "claim_006",
        "name": "Hard Case 6: Claim mixing two currencies",
        "submission_date": "2026-08-01",
        "claimant": "Fiona Gallagher",
        "stated_total": 650.0,
        "raw_text": "Claimant: Fiona Gallagher\nSubmission Date: 2026-08-01\nStated Total: 650.0 USD\nLine Items:\n1. 2026-07-20 | Travel | City Taxi | 150.0 USD | Receipt: REC-601\n2. 2026-07-21 | Meals | Euro Bistro | 500.0 EUR | Receipt: REC-602",
        "line_items": [
            {"date": "2026-07-20", "category": "Travel", "vendor": "City Taxi", "amount": 150.0, "receipt_ref": "REC-601"},
            {"date": "2026-07-21", "category": "Meals", "vendor": "Euro Bistro", "amount": 500.0, "receipt_ref": "REC-602"}
        ],
        "expected": {
            "verdict": "REJECT",
            "breaches": ["Mixed currencies detected: USD and EUR"]
        }
    },
    {
        "id": "claim_007",
        "name": "Hard Case 7: Claim under total cap containing business-class travel",
        "submission_date": "2026-08-01",
        "claimant": "George Clark",
        "stated_total": 12000.0,
        "raw_text": "Claimant: George Clark\nSubmission Date: 2026-08-01\nStated Total: 12000.0 USD\nLine Items:\n1. 2026-07-15 | Travel | Sky Airways Business Class | 12000.0 USD | Receipt: REC-701",
        "line_items": [
            {"date": "2026-07-15", "category": "Travel", "vendor": "Sky Airways Business Class", "amount": 12000.0, "receipt_ref": "REC-701"}
        ],
        "expected": {
            "verdict": "REJECT",
            "breaches": ["Travel policy breach: Business class travel is prohibited (Economy class only)"]
        }
    },
    {
        "id": "claim_008",
        "name": "Hard Case 8: One completely clean claim that must pass",
        "submission_date": "2026-08-01",
        "claimant": "Hannah Abbott",
        "stated_total": 1300.0,
        "raw_text": "Claimant: Hannah Abbott\nSubmission Date: 2026-08-01\nStated Total: 1300.0 USD\nLine Items:\n1. 2026-07-25 | Meals | Team Lunch | 900.0 USD | Receipt: REC-801\n2. 2026-07-26 | Travel | Metro Transit | 400.0 USD | Receipt: REC-802",
        "line_items": [
            {"date": "2026-07-25", "category": "Meals", "vendor": "Team Lunch", "amount": 900.0, "receipt_ref": "REC-801"},
            {"date": "2026-07-26", "category": "Travel", "vendor": "Metro Transit", "amount": 400.0, "receipt_ref": "REC-802"}
        ],
        "expected": {
            "verdict": "APPROVE",
            "breaches": []
        }
    },

    # ----------------------------------------------------
    # REMAINING CLAIMS (Claims 9 - 30)
    # ----------------------------------------------------
    {
        "id": "claim_009",
        "name": "Clean Travel Economy Claim",
        "submission_date": "2026-08-01",
        "claimant": "Ian Malcolm",
        "stated_total": 14000.0,
        "raw_text": "Claimant: Ian Malcolm\nSubmission Date: 2026-08-01\nStated Total: 14000.0 USD\nLine Items:\n1. 2026-07-20 | Travel | Global Airlines Economy Flight | 14000.0 USD | Receipt: REC-901",
        "line_items": [
            {"date": "2026-07-20", "category": "Travel", "vendor": "Global Airlines Economy Flight", "amount": 14000.0, "receipt_ref": "REC-901"}
        ],
        "expected": {
            "verdict": "APPROVE",
            "breaches": []
        }
    },
    {
        "id": "claim_010",
        "name": "Travel limit exceeded (>15,000 per trip)",
        "submission_date": "2026-08-01",
        "claimant": "Julia Roberts",
        "stated_total": 18000.0,
        "raw_text": "Claimant: Julia Roberts\nSubmission Date: 2026-08-01\nStated Total: 18000.0 USD\nLine Items:\n1. 2026-07-15 | Travel | Transatlantic Flight Economy | 18000.0 USD | Receipt: REC-1001",
        "line_items": [
            {"date": "2026-07-15", "category": "Travel", "vendor": "Transatlantic Flight Economy", "amount": 18000.0, "receipt_ref": "REC-1001"}
        ],
        "expected": {
            "verdict": "REJECT",
            "breaches": ["Travel limit exceeded: 18000.0 (max 15,000 per trip)"]
        }
    },
    {
        "id": "claim_011",
        "name": "Total claim exceeds 50,000 cap",
        "submission_date": "2026-08-01",
        "claimant": "Kevin Spacey",
        "stated_total": 55000.0,
        "raw_text": "Claimant: Kevin Spacey\nSubmission Date: 2026-08-01\nStated Total: 55000.0 USD\nLine Items:\n1. 2026-07-10 | Equipment | Server Rack Cluster | 55000.0 USD | Receipt: REC-1101",
        "line_items": [
            {"date": "2026-07-10", "category": "Equipment", "vendor": "Server Rack Cluster", "amount": 55000.0, "receipt_ref": "REC-1101"}
        ],
        "expected": {
            "verdict": "REJECT",
            "breaches": ["Total claim cap exceeded: 55000.0 (max 50,000)"]
        }
    },
    {
        "id": "claim_012",
        "name": "Clean Software Subscription Claim",
        "submission_date": "2026-08-01",
        "claimant": "Laura Croft",
        "stated_total": 3000.0,
        "raw_text": "Claimant: Laura Croft\nSubmission Date: 2026-08-01\nStated Total: 3000.0 USD\nLine Items:\n1. 2026-07-22 | Services | Cloud Hosting Subscription | 3000.0 USD | Receipt: REC-1201",
        "line_items": [
            {"date": "2026-07-22", "category": "Services", "vendor": "Cloud Hosting Subscription", "amount": 3000.0, "receipt_ref": "REC-1201"}
        ],
        "expected": {
            "verdict": "APPROVE",
            "breaches": []
        }
    },
    {
        "id": "claim_013",
        "name": "Missing receipt for item over 5,000",
        "submission_date": "2026-08-01",
        "claimant": "Michael Scott",
        "stated_total": 5500.0,
        "raw_text": "Claimant: Michael Scott\nSubmission Date: 2026-08-01\nStated Total: 5500.0 USD\nLine Items:\n1. 2026-07-20 | Services | Consulting Fee | 5500.0 USD | Receipt: None",
        "line_items": [
            {"date": "2026-07-20", "category": "Services", "vendor": "Consulting Fee", "amount": 5500.0, "receipt_ref": None}
        ],
        "expected": {
            "verdict": "REJECT",
            "breaches": ["Missing receipt reference for item over 5,000: Consulting Fee 5500.0"]
        }
    },
    {
        "id": "claim_014",
        "name": "Expense 45 days old",
        "submission_date": "2026-08-01",
        "claimant": "Nancy Wheeler",
        "stated_total": 1200.0,
        "raw_text": "Claimant: Nancy Wheeler\nSubmission Date: 2026-08-01\nStated Total: 1200.0 USD\nLine Items:\n1. 2026-06-15 | Equipment | Office Desk Chair | 1200.0 USD | Receipt: REC-1401",
        "line_items": [
            {"date": "2026-06-15", "category": "Equipment", "vendor": "Office Desk Chair", "amount": 1200.0, "receipt_ref": "REC-1401"}
        ],
        "expected": {
            "verdict": "REJECT",
            "breaches": ["Expense date older than 30 days: 2026-06-15 submitted on 2026-08-01 (47 days)"]
        }
    },
    {
        "id": "claim_015",
        "name": "Clean Multi-item Meals & Travel Claim",
        "submission_date": "2026-08-01",
        "claimant": "Oscar Martinez",
        "stated_total": 1400.0,
        "raw_text": "Claimant: Oscar Martinez\nSubmission Date: 2026-08-01\nStated Total: 1400.0 USD\nLine Items:\n1. 2026-07-29 | Meals | Executive Diner | 1100.0 USD | Receipt: REC-1501\n2. 2026-07-30 | Travel | City Cab | 300.0 USD | Receipt: REC-1502",
        "line_items": [
            {"date": "2026-07-29", "category": "Meals", "vendor": "Executive Diner", "amount": 1100.0, "receipt_ref": "REC-1501"},
            {"date": "2026-07-30", "category": "Travel", "vendor": "City Cab", "amount": 300.0, "receipt_ref": "REC-1502"}
        ],
        "expected": {
            "verdict": "APPROVE",
            "breaches": []
        }
    },
    {
        "id": "claim_016",
        "name": "Meal daily cap exceeded (1,500 on single day)",
        "submission_date": "2026-08-01",
        "claimant": "Pam Beesly",
        "stated_total": 1500.0,
        "raw_text": "Claimant: Pam Beesly\nSubmission Date: 2026-08-01\nStated Total: 1500.0 USD\nLine Items:\n1. 2026-07-27 | Meals | Italian Trattoria | 1500.0 USD | Receipt: REC-1601",
        "line_items": [
            {"date": "2026-07-27", "category": "Meals", "vendor": "Italian Trattoria", "amount": 1500.0, "receipt_ref": "REC-1601"}
        ],
        "expected": {
            "verdict": "REVIEW",
            "breaches": ["Meal daily cap exceeded: 1500.0 at Italian Trattoria (max 1200/day)"]
        }
    },
    {
        "id": "claim_017",
        "name": "Arithmetic mismatch (stated 3500, sum 3000)",
        "submission_date": "2026-08-01",
        "claimant": "Quentin Tarantino",
        "stated_total": 3500.0,
        "raw_text": "Claimant: Quentin Tarantino\nSubmission Date: 2026-08-01\nStated Total: 3500.0 USD\nLine Items:\n1. 2026-07-20 | Services | Editing Software | 1500.0 USD | Receipt: REC-1701\n2. 2026-07-21 | Equipment | Microphones | 1500.0 USD | Receipt: REC-1702",
        "line_items": [
            {"date": "2026-07-20", "category": "Services", "vendor": "Editing Software", "amount": 1500.0, "receipt_ref": "REC-1701"},
            {"date": "2026-07-21", "category": "Equipment", "vendor": "Microphones", "amount": 1500.0, "receipt_ref": "REC-1702"}
        ],
        "expected": {
            "verdict": "REVIEW",
            "breaches": ["Arithmetic discrepancy: line items sum to 3000.0 but stated total is 3500.0"]
        }
    },
    {
        "id": "claim_018",
        "name": "Clean Office Supplies Claim",
        "submission_date": "2026-08-01",
        "claimant": "Rachel Green",
        "stated_total": 4500.0,
        "raw_text": "Claimant: Rachel Green\nSubmission Date: 2026-08-01\nStated Total: 4500.0 USD\nLine Items:\n1. 2026-07-26 | Equipment | Ergonomic Chairs | 4500.0 USD | Receipt: REC-1801",
        "line_items": [
            {"date": "2026-07-26", "category": "Equipment", "vendor": "Ergonomic Chairs", "amount": 4500.0, "receipt_ref": "REC-1801"}
        ],
        "expected": {
            "verdict": "APPROVE",
            "breaches": []
        }
    },
    {
        "id": "claim_019",
        "name": "Travel Non-Economy (First Class)",
        "submission_date": "2026-08-01",
        "claimant": "Steve Rogers",
        "stated_total": 9000.0,
        "raw_text": "Claimant: Steve Rogers\nSubmission Date: 2026-08-01\nStated Total: 9000.0 USD\nLine Items:\n1. 2026-07-18 | Travel | Pacific Air First Class | 9000.0 USD | Receipt: REC-1901",
        "line_items": [
            {"date": "2026-07-18", "category": "Travel", "vendor": "Pacific Air First Class", "amount": 9000.0, "receipt_ref": "REC-1901"}
        ],
        "expected": {
            "verdict": "REJECT",
            "breaches": ["Travel policy breach: First Class travel is prohibited (Economy class only)"]
        }
    },
    {
        "id": "claim_020",
        "name": "Double Breach: Claim cap >50k and expense 40 days old",
        "submission_date": "2026-08-01",
        "claimant": "Tony Stark",
        "stated_total": 52000.0,
        "raw_text": "Claimant: Tony Stark\nSubmission Date: 2026-08-01\nStated Total: 52000.0 USD\nLine Items:\n1. 2026-06-20 | Equipment | Quantum Processor | 52000.0 USD | Receipt: REC-2001",
        "line_items": [
            {"date": "2026-06-20", "category": "Equipment", "vendor": "Quantum Processor", "amount": 52000.0, "receipt_ref": "REC-2001"}
        ],
        "expected": {
            "verdict": "REJECT",
            "breaches": [
                "Total claim cap exceeded: 52000.0 (max 50,000)",
                "Expense date older than 30 days: 2026-06-20 submitted on 2026-08-01 (42 days)"
            ]
        }
    },
    {
        "id": "claim_021",
        "name": "Clean Client Dinner Claim",
        "submission_date": "2026-08-01",
        "claimant": "Ursula Buffay",
        "stated_total": 1150.0,
        "raw_text": "Claimant: Ursula Buffay\nSubmission Date: 2026-08-01\nStated Total: 1150.0 USD\nLine Items:\n1. 2026-07-29 | Meals | Seafood Restaurant | 1150.0 USD | Receipt: REC-2101",
        "line_items": [
            {"date": "2026-07-29", "category": "Meals", "vendor": "Seafood Restaurant", "amount": 1150.0, "receipt_ref": "REC-2101"}
        ],
        "expected": {
            "verdict": "APPROVE",
            "breaches": []
        }
    },
    {
        "id": "claim_022",
        "name": "Meal cap exceeded (1,400 on single day)",
        "submission_date": "2026-08-01",
        "claimant": "Victor Stone",
        "stated_total": 1400.0,
        "raw_text": "Claimant: Victor Stone\nSubmission Date: 2026-08-01\nStated Total: 1400.0 USD\nLine Items:\n1. 2026-07-27 | Meals | Downtown Grill | 1400.0 USD | Receipt: REC-2201",
        "line_items": [
            {"date": "2026-07-27", "category": "Meals", "vendor": "Downtown Grill", "amount": 1400.0, "receipt_ref": "REC-2201"}
        ],
        "expected": {
            "verdict": "REVIEW",
            "breaches": ["Meal daily cap exceeded: 1400.0 at Downtown Grill (max 1200/day)"]
        }
    },
    {
        "id": "claim_023",
        "name": "Item 8,000 missing receipt",
        "submission_date": "2026-08-01",
        "claimant": "Wanda Maximoff",
        "stated_total": 8000.0,
        "raw_text": "Claimant: Wanda Maximoff\nSubmission Date: 2026-08-01\nStated Total: 8000.0 USD\nLine Items:\n1. 2026-07-24 | Services | Security Audit | 8000.0 USD | Receipt: None",
        "line_items": [
            {"date": "2026-07-24", "category": "Services", "vendor": "Security Audit", "amount": 8000.0, "receipt_ref": None}
        ],
        "expected": {
            "verdict": "REJECT",
            "breaches": ["Missing receipt reference for item over 5,000: Security Audit 8000.0"]
        }
    },
    {
        "id": "claim_024",
        "name": "Clean Hotel Accommodations Claim with valid receipt",
        "submission_date": "2026-08-01",
        "claimant": "Xavier Charles",
        "stated_total": 8000.0,
        "raw_text": "Claimant: Xavier Charles\nSubmission Date: 2026-08-01\nStated Total: 8000.0 USD\nLine Items:\n1. 2026-07-21 | Travel | Grand Plaza Hotel | 8000.0 USD | Receipt: REC-2401",
        "line_items": [
            {"date": "2026-07-21", "category": "Travel", "vendor": "Grand Plaza Hotel", "amount": 8000.0, "receipt_ref": "REC-2401"}
        ],
        "expected": {
            "verdict": "APPROVE",
            "breaches": []
        }
    },
    {
        "id": "claim_025",
        "name": "Expense 35 days old",
        "submission_date": "2026-08-01",
        "claimant": "Yelena Belova",
        "stated_total": 2100.0,
        "raw_text": "Claimant: Yelena Belova\nSubmission Date: 2026-08-01\nStated Total: 2100.0 USD\nLine Items:\n1. 2026-06-27 | Services | Training Course | 2100.0 USD | Receipt: REC-2501",
        "line_items": [
            {"date": "2026-06-27", "category": "Services", "vendor": "Training Course", "amount": 2100.0, "receipt_ref": "REC-2501"}
        ],
        "expected": {
            "verdict": "REJECT",
            "breaches": ["Expense date older than 30 days: 2026-06-27 submitted on 2026-08-01 (35 days)"]
        }
    },
    {
        "id": "claim_026",
        "name": "Mixed currencies (USD and GBP)",
        "submission_date": "2026-08-01",
        "claimant": "Zack Snyder",
        "stated_total": 1200.0,
        "raw_text": "Claimant: Zack Snyder\nSubmission Date: 2026-08-01\nStated Total: 1200.0 USD\nLine Items:\n1. 2026-07-20 | Meals | London Pub | 700.0 GBP | Receipt: REC-2601\n2. 2026-07-21 | Travel | US Transit | 500.0 USD | Receipt: REC-2602",
        "line_items": [
            {"date": "2026-07-20", "category": "Meals", "vendor": "London Pub", "amount": 700.0, "receipt_ref": "REC-2601"},
            {"date": "2026-07-21", "category": "Travel", "vendor": "US Transit", "amount": 500.0, "receipt_ref": "REC-2602"}
        ],
        "expected": {
            "verdict": "REJECT",
            "breaches": ["Mixed currencies detected: USD and GBP"]
        }
    },
    {
        "id": "claim_027",
        "name": "Clean Taxi and Lunch Claim",
        "submission_date": "2026-08-01",
        "claimant": "Arthur Pendelton",
        "stated_total": 1100.0,
        "raw_text": "Claimant: Arthur Pendelton\nSubmission Date: 2026-08-01\nStated Total: 1100.0 USD\nLine Items:\n1. 2026-07-28 | Travel | Metro Cab | 600.0 USD | Receipt: REC-2701\n2. 2026-07-28 | Meals | Corner Cafe | 500.0 USD | Receipt: REC-2702",
        "line_items": [
            {"date": "2026-07-28", "category": "Travel", "vendor": "Metro Cab", "amount": 600.0, "receipt_ref": "REC-2701"},
            {"date": "2026-07-28", "category": "Meals", "vendor": "Corner Cafe", "amount": 500.0, "receipt_ref": "REC-2702"}
        ],
        "expected": {
            "verdict": "APPROVE",
            "breaches": []
        }
    },
    {
        "id": "claim_028",
        "name": "Arithmetic mismatch (stated 6500, sum 7000)",
        "submission_date": "2026-08-01",
        "claimant": "Bruce Wayne",
        "stated_total": 6500.0,
        "raw_text": "Claimant: Bruce Wayne\nSubmission Date: 2026-08-01\nStated Total: 6500.0 USD\nLine Items:\n1. 2026-07-25 | Equipment | Tech Gadgets | 4000.0 USD | Receipt: REC-2801\n2. 2026-07-26 | Services | Security Consultation | 3000.0 USD | Receipt: REC-2802",
        "line_items": [
            {"date": "2026-07-25", "category": "Equipment", "vendor": "Tech Gadgets", "amount": 4000.0, "receipt_ref": "REC-2801"},
            {"date": "2026-07-26", "category": "Services", "vendor": "Security Consultation", "amount": 3000.0, "receipt_ref": "REC-2802"}
        ],
        "expected": {
            "verdict": "REVIEW",
            "breaches": ["Arithmetic discrepancy: line items sum to 7000.0 but stated total is 6500.0"]
        }
    },
    {
        "id": "claim_029",
        "name": "Travel 16,000 exceeding 15k limit",
        "submission_date": "2026-08-01",
        "claimant": "Clark Kent",
        "stated_total": 16000.0,
        "raw_text": "Claimant: Clark Kent\nSubmission Date: 2026-08-01\nStated Total: 16000.0 USD\nLine Items:\n1. 2026-07-12 | Travel | International Flight Economy | 16000.0 USD | Receipt: REC-2901",
        "line_items": [
            {"date": "2026-07-12", "category": "Travel", "vendor": "International Flight Economy", "amount": 16000.0, "receipt_ref": "REC-2901"}
        ],
        "expected": {
            "verdict": "REJECT",
            "breaches": ["Travel limit exceeded: 16000.0 (max 15,000 per trip)"]
        }
    },
    {
        "id": "claim_030",
        "name": "Clean Train & Hotel Claim",
        "submission_date": "2026-08-01",
        "claimant": "Diana Prince",
        "stated_total": 5200.0,
        "raw_text": "Claimant: Diana Prince\nSubmission Date: 2026-08-01\nStated Total: 5200.0 USD\nLine Items:\n1. 2026-07-22 | Travel | Express Train | 1200.0 USD | Receipt: REC-3001\n2. 2026-07-23 | Travel | City Center Hotel | 4000.0 USD | Receipt: REC-3002",
        "line_items": [
            {"date": "2026-07-22", "category": "Travel", "vendor": "Express Train", "amount": 1200.0, "receipt_ref": "REC-3001"},
            {"date": "2026-07-23", "category": "Travel", "vendor": "City Center Hotel", "amount": 4000.0, "receipt_ref": "REC-3002"}
        ],
        "expected": {
            "verdict": "APPROVE",
            "breaches": []
        }
    }
]
