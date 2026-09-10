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

On 2026-09-10, the frozen v4 Seed candidate at source commit `b4242af758b1222f8ecea0bf7306e917a36ed9d8` was evaluated on a new 16-pair private holdout v4 against the exact same local `qwen3:8b` Raw control under the hard 8,000-token arm envelope.

The private v4 suite was independently audited 16/16 before inference and preregistered at commit `e346ffabb2f77bded32d29e58e8009dc2731fd20`.

Result:
- Raw: **3/16 = 18.75%**
- Seed: **11/16 = 68.75%**
- observed mean gain: **+50 percentage points**
- strict Seed win rate: **8/16 = 50.00%**
- 95% paired-bootstrap CI: **[+25.00 pp, +75.00 pp]**
- Gate-1 promotion: **FAIL** because the frozen strict-win threshold is >=60%

Pair count, mean gain, CI, identity/integrity and resource-envelope criteria all passed. With 16 pairs, promotion requires at least 10 strict Seed wins; v4 produced 8. The threshold is not weakened after observing the result.

See [`docs/GATE1_LOCAL_HOLDOUT_V4_RESULT.md`](docs/GATE1_LOCAL_HOLDOUT_V4_RESULT.md) and [`artifacts/gate1-local-holdout-v4-score.json`](artifacts/gate1-local-holdout-v4-score.json). Gate 1 remains empirically tested but **not certified**.

### Frozen v4 candidate

The evaluated v4 candidate is source commit `b4242af758b1222f8ecea0bf7306e917a36ed9d8`, implementation digest `f9d882e185b235d0a8345640ee1577edb518be96dbf8af0f6b50ec204f5a1358`. It passes **134/134** local tests and **10/10** deterministic Gate-1 checks. See [`docs/GATE1_V4_DEVELOPMENT.md`](docs/GATE1_V4_DEVELOPMENT.md).

### Current v5 candidate

v5 is frozen at source commit `c34e1cd31c61efebc513f289ba9ac11cdd4412d0`, implementation digest `011881547d85a31cccc3bd66a174e7ae9b3e8506014a6c918d248e78708e286c`. It passes **140/140** local tests and **10/10** deterministic Gate-1 checks. All five v4 both-wrong failure classes close on retired development probes. A new independently audited/preregistered private holdout v5 is required before any promotion claim. See [`docs/GATE1_V5_DEVELOPMENT.md`](docs/GATE1_V5_DEVELOPMENT.md).

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
