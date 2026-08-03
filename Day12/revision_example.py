"""
Day 12 Revision Exercise Script.
"""

import random

SEED_VALUE = 42


def generate_reproducible_split(ticket_ids: list, seed: int = 42):
    random.seed(seed)
    shuffled_ids = random.sample(ticket_ids, len(ticket_ids))
    n = len(shuffled_ids)
    train_end = int(n * 0.60)
    val_end = train_end + int(n * 0.20)
    
    train_ids = sorted(shuffled_ids[:train_end])
    val_ids = sorted(shuffled_ids[train_end:val_end])
    test_ids = sorted(shuffled_ids[val_end:])
    
    return train_ids, val_ids, test_ids


def main():
    ticket_ids = list(range(1, 31))
    t1, v1, s1 = generate_reproducible_split(ticket_ids, seed=SEED_VALUE)
    t2, v2, s2 = generate_reproducible_split(ticket_ids, seed=SEED_VALUE)
    print("Reproducibility Verification Check:", "PASS" if (t1 == t2 and v1 == v2 and s1 == s2) else "FAIL")


if __name__ == "__main__":
    main()
