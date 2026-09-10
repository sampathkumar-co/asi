# Gates 0-4

A gate has two levels of evidence:

1. **Infrastructure qualification** — the machinery behaves correctly under deterministic canaries.
2. **Empirical certification** — real model/research runs satisfy the preregistered scientific criterion on hidden/OOD evaluations.

## Gate 0 — Evaluation infrastructure

### Objective
Establish trustworthy measurement before optimization begins.

### Status
**COMPLETE / infrastructure-qualified.**

The fail-closed `seed gate0-certify` command validates external holdout separation, known-good/known-bad discrimination, statistical comparison, receipt integrity, tamper rejection and evaluator immutability.

### Scientific role
Gate 0 is the measurement instrument used to judge every later capability claim.

---

## Gate 1 — Bounded baseline agent

### Objective
Determine whether a scaffold improves a fixed model under a controlled resource envelope.

### Status
**Infrastructure-qualified and empirically tested; NOT empirically certified.**

The latest preregistered unseen 16-pair local Qwen3-8B holdout v3 completed on 2026-09-10. Raw scored 3/16 and Seed scored 11/16, a +50 percentage-point mean gain. The 95% paired-bootstrap CI for gain was [+18.75 pp, +81.25 pp], clearing zero. However strict Seed win rate was 9/16 = 56.25%, below the frozen >=60% requirement. Gate 1 therefore does not promote.

See [`GATE1_LOCAL_HOLDOUT_V3_RESULT.md`](GATE1_LOCAL_HOLDOUT_V3_RESULT.md).

Post-v3 reliability development is frozen at `b4242af758b1222f8ecea0bf7306e917a36ed9d8` with implementation digest `f9d882e185b235d0a8345640ee1577edb518be96dbf8af0f6b50ec204f5a1358`; it passes **134/134** local tests and **10/10** deterministic Gate-1 checks. Retired-v3 diagnostics are development evidence only. See [`GATE1_V4_DEVELOPMENT.md`](GATE1_V4_DEVELOPMENT.md).

### Implemented
- raw-model control arm;
- planner/executor/critic Seed arm;
- persistent state/provenance;
- hard model/tool/step/token/cost budgets;
- model-call metering and transcript hashes;
- local Ollama adapter and exact model digest attestation;
- explicit relevant-tool routing and allowlists;
- exact reusable graph/scheduling/CRT, semantic transaction/reconciliation, Python-trace, subset-optimization and CSP tools;
- sandboxed computation fallback;
- fail-closed malformed-output and budget behavior;
- same-provider/same-envelope comparison evidence;
- per-pair checkpoint/resume;
- implementation digest attestation;
- external-key scoring and paired bootstrap;
- deterministic `seed gate1-certify` infrastructure canary.

### Infrastructure criterion
The qualification must prove that both arms use the same declared provider identity and envelope, that overspending and denied actions fail closed, and that the harness can detect a planted multi-step capability difference.

### Empirical criterion
Before inference, freeze the candidate implementation, exact model artifact, private task/key hashes, resource envelope and promotion thresholds. Using the same model artifact for both arms, Seed must outperform Raw on a new hidden/OOD campaign while remaining inside the common resource envelope.

The current promotion rule requires:
- at least 16 valid paired tasks;
- mean Seed capability gain >= 5 percentage points;
- strict Seed paired win rate >= 60%;
- 95% paired-bootstrap CI lower bound > 0;
- no integrity or resource-envelope violation.

A failed holdout becomes development evidence. Its tasks cannot be reused as fresh certification data after architecture changes.

---

## Gate 2 — Scientific-method and verification layer

### Objective
Make the system reason in terms of falsifiable hypotheses and independent evidence.

### Status
**Foundation implemented; not empirically certified.**

### Implemented
- hypotheses + falsifiers;
- experiments + controls;
- predicted results + success metrics;
- reproducibility flag;
- independent verifier;
- adversarial verifier.

### Empirical criterion
Reliably reject bad hypotheses, detect confounds, backtrack, and reproduce accepted results on hidden/OOD research tasks.

---

## Gate 3 — Automatic architecture search

### Objective
Search agent architectures instead of assuming a fixed human design.

### Status
**Foundation implemented; not empirically certified.**

### Implemented
- declarative `AgentGenome`;
- bounded mutations;
- archive/deduplication;
- capability-cost fitness;
- multi-generation search.

### Empirical criterion
Discovered architectures must outperform human-written baselines on new hidden/OOD suites under normalized cost.

---

## Gate 4 — Controlled self-modification

### Objective
Allow capability-plane source changes without allowing candidates to rewrite their evaluator/control plane.

### Status
**Control foundation implemented; not empirically certified.**

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
A child must pass sandbox tests, independent verification and a new hidden/OOD evaluation before human-approved promotion.
