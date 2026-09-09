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
| 1 | Strong baseline agent | Foundation implemented; empirical campaign next |
| 2 | Scientific-method / verification | Foundation implemented |
| 3 | Automatic architecture search | Foundation implemented |
| 4 | Controlled self-modification | Foundation implemented |

Gate 0 passed its fail-closed qualification on Python 3.11, 3.12 and 3.13 with **46/46 tests passing**. See [`docs/GATE0_CERTIFICATION.md`](docs/GATE0_CERTIFICATION.md) for the exact evidence and scope boundary.

## Gate-0 measurement layer

Gate 0 now provides:

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

Run it with:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
seed gate0-certify --repo-root . --output artifacts/gate0-certificate.json
```

No external LLM API is required for Gate-0 infrastructure qualification.

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

- **Gate 1:** goal/state models, persistent memory, planner/executor/critic interfaces, provider-neutral strict-JSON planner/critic, explicit budgets and tool allowlists.
- **Gate 2:** falsifiable hypotheses, experiment plans, controls, predictions, reproducibility and independent/adversarial verification.
- **Gate 3:** declarative `AgentGenome`, bounded seeded mutation, archive and capability/cost fitness search.
- **Gate 4:** copy-on-write descendants, mutation allow/deny policy, stale-hash protection, lineage, no in-place parent mutation, Docker no-network/read-only/resource limits and explicit promotion evidence.

## Gate-4 control boundary

Candidate source execution is intended to happen with network disabled, a read-only workspace, dropped Linux capabilities, `no-new-privileges`, CPU/memory/process limits and no writable parent mount. The provided Docker runner is defense-in-depth, not a formal isolation proof. Promotion remains human-approved at Gate 4.

## What Project Seed deliberately does not claim

- Gate 0 completion does not mean a frontier model has become smarter.
- It does not demonstrate recursive amplification.
- It does not demonstrate AGI or ASI.
- It does not permit candidates to rewrite the evaluator/control plane.
- It does not autonomously deploy descendants.

Those boundaries are intentional. Gate 0 gives the later experiments an instrument we can trust enough to start measuring them.

## Repository principles

1. **Measurement before optimization.** No improvement claim without reproducible evidence.
2. **Parent immutability.** Candidate descendants never rewrite the running parent in place.
3. **Evaluator separation.** Candidate code cannot modify its own evaluator by default.
4. **Hidden/OOD validation.** Visible optimization benchmarks are insufficient for promotion.
5. **Explicit resources.** Model calls, tools, tokens, cost, compute and human intervention are measured.
6. **Rollback by construction.** Descendants are separate lineage nodes.
7. **Secrets stay outside source control.** Private evals and signing keys remain control-plane inputs.
8. **Claims track evidence.** Documentation separates infrastructure qualification from empirical capability results.

For the full research thesis, see [`docs/PRIMARY_IDEA.md`](docs/PRIMARY_IDEA.md). For gate definitions and current implementation state, see [`docs/GATES.md`](docs/GATES.md) and [`docs/STATUS.md`](docs/STATUS.md).
