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
| **1** | Strong bounded baseline agent | **COMPLETE — empirically certified** |
| **2** | Scientific-method / verification | **EMPIRICALLY TESTED — NOT CERTIFIED (private v1 verifier criterion failed)** |
| 3 | Automatic architecture search | Foundation implemented; empirical campaign pending |
| 4 | Controlled self-modification | Foundation implemented; empirical campaign pending |

Gate 0 remains the trusted measurement/control instrument. Gate 1 is complete and empirically certified. Gate 2 has now completed one preregistered 18-pair private/OOD campaign: task-level transfer was strong, but the frozen verifier-acceptance criterion failed, so Gate 2 remains not empirically certified.

## Latest Gate-1 empirical result

Frozen v5 candidate: source `c34e1cd31c61efebc513f289ba9ac11cdd4412d0`, implementation digest `011881547d85a31cccc3bd66a174e7ae9b3e8506014a6c918d248e78708e286c`, local `qwen3:8b` digest `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`.

Preregistered holdout v5 result: Raw **1/16 = 6.25%**, Seed **15/16 = 93.75%**, mean gain **+87.50 pp**, strict Seed win rate **14/16 = 87.50%**, 95% paired-bootstrap CI **[+68.75 pp, +100.00 pp]**. Identity/integrity and resource-envelope audits passed. **Gate 1 promotes.**

See [`docs/GATE1_LOCAL_HOLDOUT_V5_RESULT.md`](docs/GATE1_LOCAL_HOLDOUT_V5_RESULT.md), [`docs/GATE1_LOCAL_HOLDOUT_V5_PREREGISTRATION.md`](docs/GATE1_LOCAL_HOLDOUT_V5_PREREGISTRATION.md), and [`artifacts/gate1-local-holdout-v5-score.json`](artifacts/gate1-local-holdout-v5-score.json).

Historical v2/v3/v4 campaigns remain published as failed promotion attempts. They are retired evidence and are not rewritten or reused as fresh certification data.

## Gate-2 public development calibration

The frozen Gate-2 development candidate uses local `qwen3:8b` with a common 16-call / 12,000-token envelope. Deterministic protocol qualification passes **28/28** canaries and the repository passes **157/157** tests with `ResourceWarning` treated as an error.

On the eight-task public calibration suite, Raw scored **0.78750** mean and Seed **0.93125**, a **+0.14375** mean gain. Strict Seed wins were **5/8 = 62.5%**, verifier acceptance **6/8 = 75%**, and the paired-bootstrap CI was **[-0.015625, +0.31875]**. This public run does **not** promote Gate 2: it has only 8 pairs, misses the frozen +0.15 mean-gain threshold by 0.00625, and its CI lower bound is not above zero.

The public suite is now retired as development evidence. See [`docs/GATE2_PROTOCOL.md`](docs/GATE2_PROTOCOL.md), [`docs/GATE2_DEVELOPMENT.md`](docs/GATE2_DEVELOPMENT.md), and [`docs/GATE2_CERTIFICATION.md`](docs/GATE2_CERTIFICATION.md).

## Gate-2 private holdout v1

Frozen source commit `ec1e98315a0baa2fe47d344702790b86bbc6132f` and preregistration commit `2126f64b7d37964edf019794507cd19d021f2fd8` were both pushed with green CI before private inference.

On the 18-task balanced private/OOD holdout, Raw mean was **0.70556** and Seed mean was **0.94167**, for a **+0.23611** gain. Strict Seed wins were **12/18 = 66.67%** and the preregistered paired-bootstrap CI was **[+0.11944, +0.37222]**. Those metrics all pass.

However, Seed dual-verifier acceptance was only **9/18 = 50%**, below the frozen **75%** requirement. Therefore **Gate 2 does not promote**. The holdout is retired and cannot be reused as fresh certification evidence after any candidate change.

See [`docs/GATE2_PRIVATE_HOLDOUT_V1_RESULT.md`](docs/GATE2_PRIVATE_HOLDOUT_V1_RESULT.md) and [`artifacts/gate2-private-holdout-v1-score.json`](artifacts/gate2-private-holdout-v1-score.json).

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
- **Gate 2:** falsifiable action selection; isolated blind per-hypothesis forecasts; optional two-way forecast-collision audit; reveal-then-mechanical comparison; explicit evidence-driven revision; bounded repair; independent/adversarial verification; runner-derived verdicts; attested paired campaigns.
- **Gate 3:** declarative `AgentGenome`, bounded seeded mutation, archive and capability/cost fitness search.
- **Gate 4:** copy-on-write descendants, mutation allow/deny policy, stale-hash protection, lineage, no in-place parent mutation, Docker no-network/read-only/resource limits and explicit promotion evidence.

## Gate-4 control boundary

Candidate source execution is intended to happen with network disabled, a read-only workspace, dropped Linux capabilities, `no-new-privileges`, CPU/memory/process limits and no writable parent mount. The provided Docker runner is defense-in-depth, not a formal isolation proof. Promotion remains human-approved at Gate 4.

## What Project Seed deliberately does not claim

- Gate 0 completion does not mean a frontier model has become smarter.
- Gate 1 is empirically certified; Gate 2 is **not** yet empirically certified and its eight-task public calibration is development evidence only.
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
