# Project Seed

Project Seed is a controlled research foundation for a specific question:

> **If we improve an AI system, does that improvement make the system better at producing its next verified capability improvement?**

The project does **not** claim to be AGI or ASI. Its purpose is to make recursive-improvement claims measurable, reproducible, and falsifiable.

## Primary idea

Most agent systems optimize task performance. Project Seed additionally measures **metaproductivity**: how productive the system is at creating verified improvements to itself or its descendants.

Let:

- `C_t` = measured capability of generation `t`
- `R_t` = verified capability gain produced per unit of research/compute/human cost at generation `t`
- `M_t = R_(t+1) / R_t` = recursive amplification ratio

Interpretation:

- `M < 1`: diminishing returns
- `M ~= 1`: ordinary iterative engineering
- `M > 1` sustained on hidden/out-of-distribution tests: evidence of recursive acceleration

The most important engineering rule is that **the system being optimized is less privileged than the evaluator and control plane**. A candidate may propose changes, but it cannot silently change the metric, security policy, or parent that judges it.

## Current scope: Gates 0-4

| Gate | Purpose | Implemented foundation |
|---|---|---|
| 0 | Measurement before optimization | Eval suites, bounded scorers, repeated-run statistics, private-holdout loader, receipts, hash-chain event log, efficiency/metaproductivity metrics |
| 1 | Strong baseline agent loop | Goal/state model, persistent memory, planner/executor/critic interfaces, strict provider-neutral JSON planner/critic, explicit budgets, tool allowlist, deterministic baseline |
| 2 | Scientific-method workflow | Hypothesis, falsifiers, experiment plans, reproducibility flag, independent + adversarial verification |
| 3 | Automatic architecture discovery | Declarative `AgentGenome`, bounded evolutionary mutations, archive, capability/cost fitness |
| 4 | Controlled self-modification | Copy-on-write descendants, immutable path policy, stale-write protection, no in-place parent mutation, durable lineage, Docker no-network sandbox, promotion evidence gate |

See [`docs/PRIMARY_IDEA.md`](docs/PRIMARY_IDEA.md), [`docs/GATES.md`](docs/GATES.md), and [`docs/STATUS.md`](docs/STATUS.md) for the detailed design and exact implementation status.

## Architecture

```text
                           CONTROL PLANE
              +----------------------------------+
              | immutable evals / policy / logs |
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
                                                        | hidden evaluation |
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

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
seed eval-demo
seed demo
seed search-demo
```

No external LLM API is required for the deterministic foundation tests.

## Gate 4 sandbox

Candidate source execution is intended to happen in Docker with:

- network disabled;
- read-only workspace;
- all Linux capabilities dropped;
- `no-new-privileges`;
- CPU, memory and process limits;
- ephemeral tmpfs;
- parent repo never mounted writable.

The provided Docker sandbox is **defense-in-depth, not a formal isolation proof**. Promotion should remain human-approved until stronger isolation/evaluation is demonstrated.

## What Project Seed deliberately does not do yet

- modify foundation-model weights;
- autonomously deploy itself;
- grant descendants unrestricted shell/network access;
- allow candidates to modify the evaluation/control plane;
- claim that benchmark gains imply general intelligence;
- claim that recursive amplification has been demonstrated.

Those omissions are intentional. Gates 0-4 are the measurement/control foundation required before harder experiments are scientifically meaningful.

## Repository principles

1. **Measurement before optimization.** No improvement claim without a reproducible receipt.
2. **Parent immutability.** Candidate descendants never rewrite the running parent in place.
3. **Evaluator separation.** Optimization code cannot modify its own evaluator by default.
4. **Hidden/OOD validation.** Visible training benchmarks are not sufficient for promotion.
5. **Explicit budgets.** Every run has bounded steps, tool calls, tokens, cost and eventually compute.
6. **Rollback by construction.** Descendants are archived separately; promotion is an explicit decision.
7. **No secret-dependent tests.** Credentials stay outside the repository.
8. **Claims track evidence.** `docs/STATUS.md` distinguishes implemented, tested, designed and future work.

## Status

Current foundation release: **v0.1 / Gates 0-4 foundation**.

This means the infrastructure exists and is tested. It does **not** mean Gate 0-4 research criteria have all been scientifically certified on frontier models; those empirical campaigns come next.
