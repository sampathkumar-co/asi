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

Latest unseen holdout result (v3):
- Raw 3/16 (18.75%);
- Seed 11/16 (68.75%);
- +50 percentage-point observed gain;
- 9/16 = 56.25% strict Seed win rate;
- 95% paired-bootstrap CI [+18.75 pp, +81.25 pp];
- **promotion FAIL** only because the frozen >=60% strict-win criterion was not met.

### Milestone A2 — vNext / holdout-v3 cycle

**Status: completed; promotion not passed.**

The vNext candidate at `83ec193d6300b0658af8d4d3c45109880b28363f` substantially improved unseen accuracy and moved the confidence interval fully above zero. Holdout v3 is now retired to development use. Full result: [`GATE1_LOCAL_HOLDOUT_V3_RESULT.md`](GATE1_LOCAL_HOLDOUT_V3_RESULT.md).

### Milestone A3 — Gate-1 v4 candidate

**Status: candidate frozen; new holdout v4 not yet generated.**

Post-v3 reliability work is frozen at `b4242af758b1222f8ecea0bf7306e917a36ed9d8`, implementation digest `f9d882e185b235d0a8345640ee1577edb518be96dbf8af0f6b50ec204f5a1358`. Local validation is **134/134** and deterministic Gate-1 qualification is **10/10**. Retired-v3 probes close the targeted graph-routing and assignment/CSP failures; they remain development evidence only.

Before another promotion attempt:
1. generate a **new** private holdout v4 with materially different instances;
2. independently audit correctness, uniqueness and optimality;
3. preregister task/key hashes, model digest, candidate digest, envelope and thresholds;
4. run all pairs without architecture changes;
5. score once and publish the result even if it fails.

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
