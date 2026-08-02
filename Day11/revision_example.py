import textwrap

def build_dedented_prompt(ticket_text: str) -> str:
    prompt = textwrap.dedent(f"""
        [SYSTEM]
        Identity: Customer Support Ticket Classifier.
        
        [USER]
        Ticket: {ticket_text}
    """).strip()
    return prompt

if __name__ == "__main__":
    sample = "Payment failed on checkout page."
    print(build_dedented_prompt(sample))
