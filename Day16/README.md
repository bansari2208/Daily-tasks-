# Day 16 - Reasoning Techniques and Task Decomposition

## What I Worked On

Today I worked on the Expense Claim Review task.

I created a 30-claim evaluation set and compared two approaches:
1. Single Prompt
2. Decomposed Pipeline

## Evaluation Set

- Created 30 expense claims.
- Included 8 required hard cases.
- Manually defined the expected verdict and breached rules.
- Created a scoring function to compare actual and expected results.

## Single Prompt

The single prompt performs the complete expense claim review in one LLM call.

It checks:
- Expense items
- Arithmetic
- Expense rules
- Breaches
- Final verdict

The single prompt was connected to Langfuse for tracing and monitoring.

## Decomposed Pipeline

I divided the task into four simple stages:

1. Extract expense items
2. Check arithmetic
3. Apply expense rules
4. Decide the final verdict

TypedDicts are used to pass structured data between the stages.

## Langfuse Integration

Each stage is connected to a Langfuse prompt.

Prompts used:

- expense_single
- expense_extract_items
- expense_check_arithmetic
- expense_apply_rules
- expense_decide_verdict

Langfuse is used to view:

- Prompt versions
- Inputs and outputs
- Traces
- Token usage
- Latency
- Cost

The decomposed pipeline has one parent trace:

decomposed_claim_pipeline

with four child generations:

- expense_extract_items
- expense_check_arithmetic
- expense_apply_rules
- expense_decide_verdict

## Benchmark Results

| Metric | Single Prompt | Decomposed Pipeline |
|---|---:|---:|
| Verdict Accuracy | 83.33% | 83.33% |
| Breach Accuracy | 96.67% | 96.67% |
| Overall Accuracy | 83.33% | 83.33% |
| Average Latency | 10.90 ms | 26.68 ms |
| P95 Latency | 10.96 ms | 28.33 ms |
| Total Cost | $0.0105 | $0.0216 |
| Cost / 1,000 Claims | $0.35 | $0.72 |

## What I Learned

- A complex task can be divided into smaller stages.
- Typed handoffs make the data between stages clear.
- Langfuse helps track each LLM call separately.
- Decomposition makes it easier to identify which stage caused a problem.
- Multiple LLM calls can increase latency and cost.

## Today's Status

Completed 50% of Day 16.

Completed:
- 30-claim evaluation set
- 8 hard cases
- Ground truth
- Scoring function
- TypedDicts
- Single prompt
- Decomposed pipeline
- Langfuse prompt integration
- Langfuse tracing
- 30 single-prompt runs
- 30 decomposed runs
- Accuracy measurement
- Latency measurement
- Cost measurement
- P95 latency calculation

## Remaining Work

Do not implement these tasks today. They are for the remaining Day 16 work:

- Chain-of-thought comparison
- Two-call reasoning + structured output
- Self-consistency
- Tree-of-thought / plan-and-execute
- Budget optimization
