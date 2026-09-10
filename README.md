# Project Seed

Project Seed is a controlled research system for one central question:

> **If we improve an AI system, does that improvement make the system better at producing its next verified capability improvement?**

The project does **not** claim to be AGI or ASI. Its purpose is to make recursive-improvement claims measurable, reproducible and falsifiable.

## Primary idea

Most agent systems optimize task performance. Project Seed additionally measures **metaproductivity**: how productive the system is at creating verified improvements to itself or its descendants.

Let:

- `C_t` = measured capability of generation `t`
- `R_t` = verified capability gain produced per unit of research/compute/human cost at generation `t`
- `M_t = R_(t+1) / R_t` = recursive amplification ratio

Interpretation:

- `M < 1`: diminishing returns
- `M ~= 1`: ordinary iterative engineering
- sustained `M > 1` on hidden/OOD tests under normalized resources: evidence worth investigating as recursive acceleration

The core engineering rule is that **the system being optimized is less privileged than the evaluator and control plane**. A candidate may propose changes, but it cannot silently change the metric, security policy, private holdouts or parent that judges it.

## Gate status

| Gate | Purpose | Status |
|---|---|---|
| **0** | Measurement before optimization | **COMPLETE — infrastructure-qualified** |
| **1** | Strong bounded baseline agent | **Empirically tested; promotion NOT passed** |
| 2 | Scientific-method / verification | Foundation implemented; empirical campaign pending |
| 3 | Automatic architecture search | Foundation implemented; empirical campaign pending |
| 4 | Controlled self-modification | Foundation implemented; empirical campaign pending |

Gate 0 passed its fail-closed qualification and remains the measurement/control instrument for later gates. Gate 1 has now been tested on a preregistered unseen local-model holdout, but the frozen promotion rule was not satisfied.

## Latest Gate-1 empirical result

On 2026-09-10, the frozen vNext Seed candidate at source commit `83ec193d6300b0658af8d4d3c45109880b28363f` was evaluated on a new 16-pair private holdout v3 against the exact same local `qwen3:8b` Raw control and hard 8,000-token arm envelope.

The final v3 task/key hashes were independently audited 16/16 before inference and preregistered in GitHub commit `f10457f41d167551657e7e0e2b7741f79ed25b7b`.

Result:

- Raw: **3/16 = 18.75%**
- Seed: **11/16 = 68.75%**
- observed mean gain: **+50 percentage points**
- strict Seed win rate: **9/16 = 56.25%**
- 95% paired-bootstrap CI for gain: **[+18.75 pp, +81.25 pp]**
- Gate-1 promotion: **FAIL** because the frozen strict-win threshold is >=60%

All other frozen criteria passed, including pair count, mean gain, CI lower bound >0, identity/integrity, and resource-envelope checks. With 16 pairs the win-rate threshold requires 10 strict Seed wins; v3 produced 9. The threshold is not weakened after observing the result.

See [`docs/GATE1_LOCAL_HOLDOUT_V3_RESULT.md`](docs/GATE1_LOCAL_HOLDOUT_V3_RESULT.md) and [`artifacts/gate1-local-holdout-v3-score.json`](artifacts/gate1-local-holdout-v3-score.json). Gate 1 therefore remains empirically tested but **not certified**.

## Gate-0 measurement layer

Gate 0 provides:

- external private/OOD holdout loading;
- repeated evaluation and confidence summaries;
- paired bootstrap comparisons;
- SHA-256 receipts;
- trusted-control-plane receipt signing/verification;
- evaluator-tree integrity snapshots;
- tamper rejection;
- known-good / known-bad fail-closed qualification canaries;
- explicit model/tool/token/API-cost/human/compute resource accounting;
- a machine-readable qualification certificate.

Run the repository checks with:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
seed gate0-certify --repo-root . --output artifacts/gate0-certificate.json
```

No external LLM API is required for Gate-0 infrastructure qualification. Gate-1 local experiments can use an Ollama model through the provider adapter.

## Architecture

```text
                           CONTROL PLANE
              +----------------------------------+
              | policy / private evals / signing |
              +----------------+-----------------+
                               |
                               v
+---------+   +---------+   +---------+   +-------------+
|  Goal   |-->| Planner |-->|Executor |-->| Observation |
+---------+   +---------+   +---------+   +------+------+
                                                   |
                                                   v
                                             +-----------+
                                             |  Critic   |
                                             +-----+-----+
                                                   |
                                     +-------------+-------------+
                                     |                           |
                                     v                           v
                               continue/replan                candidate
                                                                   |
                                                                   v
                                                        +------------------+
                                                        | hidden/OOD eval  |
                                                        +--------+---------+
                                                                 |
                                                       verified improvement?
                                                         /              \
                                                       no                yes
                                                       |                  |
                                                     reject          archive child
                                                                          |
                                                                          +----> next generation
```

## Gates 1-4 foundation

- **Gate 1:** provider-neutral model interface; local Ollama adapter; goal/state models; planner/executor/critic loop; deterministic relevant-tool routing; persistent provenance; implementation/model attestation; strict evidence-only critic; exact reusable tools for graphs, scheduling, CRT, semantic transactions/reconciliation, aggregation, assignment/CSP, exact Python tracing and constrained subset optimization; sandboxed computation fallback; hard budgets and checkpointed paired campaigns.
- **Gate 2:** falsifiable hypotheses, experiment plans, controls, predictions, reproducibility and independent/adversarial verification.
- **Gate 3:** declarative `AgentGenome`, bounded seeded mutation, archive and capability/cost fitness search.
- **Gate 4:** copy-on-write descendants, mutation allow/deny policy, stale-hash protection, lineage, no in-place parent mutation, Docker no-network/read-only/resource limits and explicit promotion evidence.

## Gate-4 control boundary

Candidate source execution is intended to happen with network disabled, a read-only workspace, dropped Linux capabilities, `no-new-privileges`, CPU/memory/process limits and no writable parent mount. The provided Docker runner is defense-in-depth, not a formal isolation proof. Promotion remains human-approved at Gate 4.

## What Project Seed deliberately does not claim

- Gate 0 completion does not mean a frontier model has become smarter.
- The current Gate-1 experiments do not meet the preregistered empirical promotion threshold.
- A positive task-level capability delta is not evidence of recursive amplification.
- The project does not demonstrate AGI or ASI.
- Candidates do not get to rewrite their evaluator/control plane.
- Descendants are not autonomously deployed.

## Repository principles

1. **Measurement before optimization.** No improvement claim without reproducible evidence.
2. **Parent immutability.** Candidate descendants never rewrite the running parent in place.
3. **Evaluator separation.** Candidate code cannot modify its own evaluator by default.
4. **Hidden/OOD validation.** Visible optimization benchmarks are insufficient for promotion.
5. **Explicit resources.** Model calls, tools, tokens, cost, compute and human intervention are measured.
6. **Rollback by construction.** Descendants are separate lineage nodes.
7. **Secrets stay outside source control.** Private evals and signing keys remain control-plane inputs.
8. **Claims track evidence.** Documentation separates infrastructure qualification, development calibration and empirical certification.
9. **Preregistration before holdout inference.** Candidate identity, model artifact, task/key hashes and thresholds are frozen before a certification attempt.
10. **Failed gates remain failed.** Positive sub-results are retained as evidence without weakening frozen promotion criteria after the fact.

For the full research thesis, see [`docs/PRIMARY_IDEA.md`](docs/PRIMARY_IDEA.md). For gate definitions and current implementation state, see [`docs/GATES.md`](docs/GATES.md), [`docs/STATUS.md`](docs/STATUS.md), and [`docs/ROADMAP.md`](docs/ROADMAP.md).
