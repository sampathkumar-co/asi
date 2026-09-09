# Primary Idea: Measure Recursive Capability Amplification

## 1. Research question

Project Seed exists to test one proposition:

> Does making an AI system more capable increase its ability to discover, implement, and verify the next capability improvement?

This is stronger than asking whether an agent can improve a benchmark score. A system can become better at a fixed benchmark while becoming no better at AI research, architecture discovery, debugging, experimentation, or self-improvement.

Project Seed therefore separates **task capability** from **improvement capability**.

## 2. Core quantities

For generation `t`:

- `C_t`: broad measured task capability
- `G_t = C_(t+1) - C_t`: verified capability gain
- `K_t`: external cost of producing the gain (compute + experiments + human intervention)
- `R_t = G_t / K_t`: metaproductivity
- `M_t = R_(t+1) / R_t`: recursive amplification ratio

`M_t` is the key research quantity. A one-off `M > 1` is not enough. Interesting evidence would require sustained improvement across generations, hidden tests, domain shifts, and fixed/normalized external resource budgets.

## 3. Why ordinary agent benchmarks are insufficient

A benchmark gain may come from:

- memorization;
- evaluator leakage;
- benchmark-specific hacks;
- increased inference cost;
- hidden human intervention;
- exploiting bugs in the grader;
- overfitting the visible suite.

Project Seed records cost and evaluation evidence separately so that a "better" child cannot be defined merely as "the child obtained a larger public score."

## 4. Privilege separation

The architecture has three conceptual planes:

### Capability plane
The agent, planner, memory, tool policies and candidate architectures being improved.

### Evaluation plane
Suites, hidden holdouts, scoring logic, receipts, reproducibility checks and statistical comparison.

### Control plane
Resource limits, mutation policy, sandboxing, promotion rules, rollback, audit logs and human approval.

The capability plane may evolve. The evaluation/control planes are deliberately outside the candidate mutation allowlist.

## 5. Descendants, not in-place rewriting

Project Seed models self-improvement as a lineage:

```text
A0
|- A1
|- A2
   |- A4
   `- A5
`- A3
```

A running parent proposes a candidate. A separate workspace is constructed, evaluated and either rejected or archived. This avoids the fragile pattern:

```text
running process -> rewrites itself -> evaluator state changes -> provenance lost
```

Lineage allows rollback, A/B testing, independent re-evaluation and retrospective audits.

## 6. What would count as progress

Evidence becomes stronger in this order:

1. better visible benchmark score;
2. better hidden score;
3. better out-of-distribution score;
4. better score per unit cost;
5. repeated descendants generated with low human intervention;
6. descendants become better at proposing successful descendants;
7. metaproductivity increases across multiple generations under normalized resources.

Only items 6-7 directly address recursive amplification.

## 7. What would falsify the strong hypothesis

Project Seed should be allowed to discover that recursive acceleration does not occur. Examples:

- improvement rate plateaus;
- candidate research quality does not increase with capability;
- gains require proportionally increasing external compute;
- improvements fail to transfer outside the optimization domain;
- evaluator gaming dominates genuine improvement;
- human intervention remains the actual bottleneck;
- descendants become more capable but not more metaproductive.

A negative result is useful: it distinguishes strong automated engineering from recursive intelligence amplification.

## 8. Why Gates 0-4 come first

Open-ended self-improvement without trustworthy measurement is scientifically ambiguous and operationally risky. Gates 0-4 deliberately build the instruments before attempting more autonomous research loops.
