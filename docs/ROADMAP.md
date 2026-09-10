# Roadmap after the Gates 0-4 foundation

Updated: 2026-09-10

## Milestone A — Empirical Gate 0/1 baseline

**Status: active; empirical Gate-1 promotion not yet passed.**

Completed:
- provider-neutral model interface and local Ollama adapter;
- private multi-domain holdout workflow;
- same-model Raw-vs-Seed paired campaigns under hard budgets;
- task/key/model/candidate preregistration before holdout inference;
- implementation/model/evidence hashing and checkpointing;
- public score-only result artifacts;
- one full calibration campaign and one independent preregistered unseen holdout;
- exact reusable tools for shortest paths, project critical paths, CRT, aggregation and assignment/CSP;
- deterministic relevant-tool routing and sandboxed computation fallback.

Latest unseen holdout result:
- Raw 1/16 (6.25%);
- Seed 5/16 (31.25%);
- +25 percentage-point observed gain;
- 31.25% strict Seed win rate;
- 95% paired-bootstrap CI [0.00, 0.50];
- **promotion FAIL** under the frozen >=60% win-rate and CI-low >0 rule.

### Milestone A2 — next Gate-1 candidate

Use H01-H16 only as development evidence. Do not reuse it as fresh certification data.

Priorities:
- improve critical-path translation/revision without task-specific hints;
- strengthen ledger/reconciliation mapping of status/sign/discount semantics;
- add a generic exact code-trace/state-transition capability rather than repeated free-form Python reasoning;
- make constrained optimization more direct and budget-efficient;
- improve assignment/output-format fidelity without leaking benchmark answers;
- add generic stagnation detection so repeated identical plans terminate/re-route earlier;
- preserve strict evidence-only finalization and fail-closed behavior;
- measure capability gain and resource efficiency together.

Before the next promotion attempt:
1. freeze the new candidate source + implementation digest;
2. generate a **new** private holdout with materially different instances;
3. independently audit answer correctness and uniqueness;
4. preregister task/key hashes, model digest, envelope and unchanged thresholds;
5. run all paired tasks without architecture changes;
6. score once and publish the result even if it fails.

## Milestone B — Gate 2 research benchmark

Gate-2 machinery exists, but its promotion campaign remains blocked behind a reliable Gate-1 baseline.

Planned:
- uncertain problems that require hypothesis revision;
- planted confounds and faulty instrumentation;
- replication runs;
- verifier-disagreement analysis;
- hidden/OOD scientific-method scoring.

## Milestone C — Gate 3 architecture campaign

Planned:
- broaden the genome only after Gate-1 measurement is stable;
- Pareto search across capability/cost/reliability;
- require OOD transfer before archiving a winner;
- measure search-overhead amortization;
- reject candidate architectures that improve visible development tasks but fail new holdouts.

## Milestone D — Gate 4 descendant campaign

Planned:
- preloaded sandbox images;
- immutable lineage store;
- signed candidate/eval artifacts;
- human approval UI;
- rollback rehearsal;
- reward-hacking canaries;
- new hidden/OOD qualification for every promoted child.

## Only after Gates 0-4 are empirically passed

Begin Gate 5 experiments in open-ended curriculum generation. Successful tool use, source mutation or a positive task-level delta alone must not be interpreted as evidence of recursive intelligence amplification.
