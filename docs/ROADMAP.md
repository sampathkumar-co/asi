# Roadmap after the Gates 0-4 foundation

Updated: 2026-09-11

## Milestone A — Empirical Gate 0/1 baseline

**Status: COMPLETE — Gate 1 promoted.**

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

Latest unseen holdout result (v5):
- Raw **1/16 = 6.25%**;
- Seed **15/16 = 93.75%**;
- **+87.50 percentage-point** observed gain;
- **14/16 = 87.50%** strict Seed win rate;
- 95% paired-bootstrap CI **[+68.75 pp, +100.00 pp]**;
- all identity/integrity/resource criteria passed;
- **Gate 1 COMPLETE / PROMOTED**.

v2-v4 remain historical failed promotion attempts and retired evidence.

### Milestone A2 — vNext / holdout-v3 cycle

**Status: completed; promotion not passed.**

The vNext candidate at `83ec193d6300b0658af8d4d3c45109880b28363f` substantially improved unseen accuracy and moved the confidence interval fully above zero. Holdout v3 is retired development evidence. Full result: [`GATE1_LOCAL_HOLDOUT_V3_RESULT.md`](GATE1_LOCAL_HOLDOUT_V3_RESULT.md).

### Milestone A3 — Gate-1 v4 cycle

**Status: completed; promotion not passed.**

The post-v3 reliability candidate at `b4242af758b1222f8ecea0bf7306e917a36ed9d8` passed **134/134** local tests and **10/10** deterministic qualification checks. Holdout v4 was independently audited 16/16 and preregistered before inference. It reproduced Seed 11/16 vs Raw 3/16 and a +50 pp gain with CI fully above zero, but strict Seed wins were only 8/16. Full result: [`GATE1_LOCAL_HOLDOUT_V4_RESULT.md`](GATE1_LOCAL_HOLDOUT_V4_RESULT.md).

### Milestone A4 - Gate-1 v5 promotion

**Status: COMPLETE — Gate 1 promoted.**

Frozen v5 source `c34e1cd31c61efebc513f289ba9ac11cdd4412d0`, implementation digest `011881547d85a31cccc3bd66a174e7ae9b3e8506014a6c918d248e78708e286c`, passed **140/140** local tests and **10/10** deterministic qualification checks. Holdout v5 was independently audited before inference, preregistered at `857aa0f4cac7437deb86646e6f72d682b16d806a`, and passed every frozen empirical criterion. See [`GATE1_LOCAL_HOLDOUT_V5_RESULT.md`](GATE1_LOCAL_HOLDOUT_V5_RESULT.md).

## Milestone B — Gate 2 research benchmark

**Status: EMPIRICALLY TESTED TWICE; PRIVATE V1 AND V2 FAILED DIFFERENT FROZEN CRITERIA; NOT CERTIFIED.**

Private v1 transferred strongly but failed verifier acceptance: Raw **0.70556**, Seed **0.94167**, gain **+0.23611**, strict wins **66.67%**, CI **[+0.11944, +0.37222]**, verifier acceptance **50%**.

Private v2 fixed verifier acceptance but failed transfer: Raw **0.81250**, Seed **0.82083**, gain **+0.00833**, strict wins **33.33%**, CI **[-0.07361, +0.09583]**, verifier acceptance **88.89%**.

Both holdouts are permanently retired. V3 development must target genuine Raw-to-Seed capability gain on new development tasks. Any future certification requires a newly frozen candidate and a completely new audited/preregistered private/OOD holdout.

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
