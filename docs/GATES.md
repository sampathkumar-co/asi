# Gates 0-4

A **gate** is both an engineering capability and a promotion criterion. Implementing the code for a gate is not the same as scientifically passing the gate.

## Gate 0 — Evaluation infrastructure

### Objective
Establish trustworthy measurement before optimization begins.

### Implemented
- `EvalCase` and bounded scorer abstraction
- `EvalSuite` runner
- per-case and aggregate scores
- evaluation receipts with SHA-256 content hashes
- append-only SQLite event store with per-run hash chain
- capability/efficiency metrics
- metaproductivity and recursive-amplification calculations

### Required before empirical certification
- private holdout set stored outside candidate-readable workspace
- OOD suites covering multiple task families
- repeated runs / variance estimates for stochastic models
- evaluator-leakage tests
- baseline frontier-model measurements

### Stop condition
Do not call any candidate "improved" if evaluation provenance is missing or the candidate could modify the relevant evaluator.

---

## Gate 1 — Bounded baseline agent

### Objective
Create a clear, measurable baseline before adding architectural complexity.

### Implemented
- `Goal`, `Task`, `Observation`, `AgentState`
- planner/executor/critic interfaces
- deterministic queue planner
- explicit tool registry/allowlist
- safe arithmetic and echo demonstration tools
- step/tool/model/token/cost budget object
- state/event logging
- explicit success and budget-exhausted states

### Next empirical work
Integrate one or more real model providers behind the provider-neutral interface and measure improvement relative to raw-model baselines.

### Gate criterion
The scaffold must improve performance on long-horizon hidden tasks at acceptable normalized cost—not merely consume more inference.

---

## Gate 2 — Scientific-method and verification layer

### Objective
Make the system reason in terms of falsifiable hypotheses and independent evidence.

### Implemented
- hypothesis + rationale + explicit falsifiers
- experiment plan + predicted result + success metric + controls
- experiment result + artifact references + reproducibility indicator
- independent verifier
- adversarial verifier
- acceptance requires both verifiers and reproducibility

### Next empirical work
Use genuinely uncertain research tasks, planted experimental bugs, and replication tasks.

### Gate criterion
The system must reliably reject bad hypotheses, detect confounds, backtrack, and reproduce accepted results.

---

## Gate 3 — Automatic architecture search

### Objective
Stop assuming humans know the optimal agent architecture.

### Implemented
`AgentGenome` controls:
- max reasoning steps
- verification passes
- memory limit
- critic threshold
- planner strategy

`ArchitectureSearch` provides:
- deterministic seeded mutation
- bounded parameter ranges
- candidate IDs derived from content
- archive preventing needless duplicate evaluation
- capability-cost fitness
- elitist multi-generation search

### Next work
Expand the genome carefully to model routing, context selection, memory policies, branch/merge reasoning, tool choice and stopping policies.

### Gate criterion
Discovered architectures must outperform human-written baselines on hidden/OOD suites with normalized cost.

---

## Gate 4 — Controlled self-modification

### Objective
Allow the system to propose changes to its own capability code while preserving evaluator/control integrity.

### Implemented
- structured `PatchProposal`
- file mutation allowlist
- explicit forbidden evaluator/control/provider paths
- path-traversal rejection
- mutation file/byte budgets
- optimistic concurrency via expected SHA-256
- copy-on-write descendant workspace
- no mutation of parent repository
- Docker command with no network, read-only mount, dropped capabilities, `no-new-privileges`, CPU/memory/PID limits
- explicit promotion evidence and thresholds

### Immutable by default
Candidates cannot modify:
- `.github/`
- `src/seed/eval/`
- `src/seed/selfmod/`
- `src/seed/providers/`
- control/security documentation

### Gate criterion
A child must pass sandbox tests, independent verification, hidden/OOD evaluation, and a minimum improvement threshold before promotion. Human approval remains required by policy at this stage.

---

# Promotion ladder

```text
proposal
  |
  v
policy validation ----fail----> reject
  |
 pass
  v
copy-on-write descendant
  |
  v
sandbox tests --------fail----> reject
  |
 pass
  v
visible eval
  |
  v
hidden/OOD eval ------fail----> reject
  |
 pass
  v
independent verification
  |
  v
promotion evidence
  |
  v
human approval at Gate 4
  |
  v
archive as new parent candidate
```
