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
- exact reusable tools for shortest paths, project critical paths, CRT, semantic transactions/reconciliation, aggregation, assignment/CSP, exact Python tracing and constrained subset optimization;
- deterministic relevant-tool routing and sandboxed computation fallback.

Latest unseen holdout result (v4):
- Raw 3/16 (18.75%);
- Seed 11/16 (68.75%);
- +50 percentage-point observed gain;
- 8/16 = 50.00% strict Seed win rate;
- 95% paired-bootstrap CI [+25.00 pp, +75.00 pp];
- **promotion FAIL** because the frozen >=60% strict-win criterion was not met.

### Milestone A2 — vNext / holdout-v3 cycle

**Status: completed; promotion not passed.**

The vNext candidate at `83ec193d6300b0658af8d4d3c45109880b28363f` substantially improved unseen accuracy and moved the confidence interval fully above zero. Holdout v3 is retired development evidence. Full result: [`GATE1_LOCAL_HOLDOUT_V3_RESULT.md`](GATE1_LOCAL_HOLDOUT_V3_RESULT.md).

### Milestone A3 — Gate-1 v4 cycle

**Status: completed; promotion not passed.**

The post-v3 reliability candidate at `b4242af758b1222f8ecea0bf7306e917a36ed9d8` passed **134/134** local tests and **10/10** deterministic qualification checks. Holdout v4 was independently audited 16/16 and preregistered before inference. It reproduced Seed 11/16 vs Raw 3/16 and a +50 pp gain with CI fully above zero, but strict Seed wins were only 8/16. Full result: [`GATE1_LOCAL_HOLDOUT_V4_RESULT.md`](GATE1_LOCAL_HOLDOUT_V4_RESULT.md).

### Milestone A4 - Gate-1 v5 candidate

**Status: candidate frozen; holdout-v5 preparation next.**

v5 source `c34e1cd31c61efebc513f289ba9ac11cdd4412d0`, implementation digest `011881547d85a31cccc3bd66a174e7ae9b3e8506014a6c918d248e78708e286c`, passes **140/140** local tests and **10/10** deterministic qualification checks. All five v4 both-wrong failure classes close on retired development probes. Next: generate a new private holdout v5, independently audit it, preregister identities/criteria, run unchanged, and publish the score. See [`GATE1_V5_DEVELOPMENT.md`](GATE1_V5_DEVELOPMENT.md).

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
