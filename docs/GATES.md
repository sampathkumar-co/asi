# Gates 0-4

A gate has two levels of evidence:

1. **Infrastructure qualification** — the machinery behaves correctly under deterministic canaries.
2. **Empirical certification** — real model/research runs satisfy the scientific criterion on hidden/OOD evaluations.

## Gate 0 — Evaluation infrastructure

### Objective
Establish trustworthy measurement before optimization begins.

### Status
**Infrastructure-qualified.**

The fail-closed `seed gate0-certify` command validates external holdout separation, known-good/known-bad discrimination, statistical comparison, receipt integrity, tamper rejection and evaluator immutability.

### Scientific role
Gate 0 is the measurement instrument used to judge every later capability claim.

---

## Gate 1 — Bounded baseline agent

### Objective
Determine whether a scaffold improves a fixed model under a controlled resource envelope.

### Implemented
- raw-model control arm;
- planner/executor/critic Seed arm;
- persistent state/provenance;
- hard model/tool/step/token/cost budgets;
- model-call metering and transcript hashes;
- explicit tool allowlist;
- fail-closed malformed-output and budget behavior;
- same-provider/same-envelope comparison evidence;
- deterministic `seed gate1-certify` canary.

### Infrastructure criterion
The qualification must prove that both arms use the same declared provider identity and envelope, that overspending and denied actions fail closed, and that the harness can detect a planted multi-step capability difference.

### Empirical criterion
Using the same real model/version for both arms, Seed must outperform the raw arm on repeated hidden/OOD long-horizon tasks while remaining within the common resource envelope and showing acceptable normalized efficiency.

---

## Gate 2 — Scientific-method and verification layer

### Objective
Make the system reason in terms of falsifiable hypotheses and independent evidence.

### Implemented
- hypotheses + falsifiers;
- experiments + controls;
- predicted results + success metrics;
- reproducibility flag;
- independent verifier;
- adversarial verifier.

### Empirical criterion
Reliably reject bad hypotheses, detect confounds, backtrack, and reproduce accepted results.

---

## Gate 3 — Automatic architecture search

### Objective
Search agent architectures instead of assuming a fixed human design.

### Implemented
- declarative `AgentGenome`;
- bounded mutations;
- archive/deduplication;
- capability-cost fitness;
- multi-generation search.

### Empirical criterion
Discovered architectures must outperform human-written baselines on hidden/OOD suites under normalized cost.

---

## Gate 4 — Controlled self-modification

### Objective
Allow capability-plane source changes without allowing candidates to rewrite their evaluator/control plane.

### Implemented
- structured patches;
- path/byte/file mutation limits;
- evaluator/control/provider denial paths;
- stale-hash protection;
- copy-on-write descendants;
- durable lineage;
- no-network/read-only Docker execution;
- explicit promotion evidence gate.

### Empirical criterion
A child must pass sandbox tests, independent verification and hidden/OOD evaluation before human-approved promotion.
