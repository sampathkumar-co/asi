# Roadmap after the Gates 0-4 foundation

Updated: 2026-09-13

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

**Status: V3.1 PRIVATE V31 COMPLETED - FAILED FROZEN MEAN-GAIN CRITERION; GATE 2 NOT CERTIFIED.**

Private v1 transferred strongly but failed verifier acceptance: Raw **0.70556**, Seed **0.94167**, gain **+0.23611**, strict wins **66.67%**, CI **[+0.11944, +0.37222]**, verifier acceptance **50%**. Private v2 fixed verifier acceptance but failed transfer: Raw **0.81250**, Seed **0.82083**, gain **+0.00833**, strict wins **33.33%**, CI **[-0.07361, +0.09583]**, verifier acceptance **88.89%**. Both are retired.

V3.1 uses hidden-safe outcome-to-hypothesis attribution plus runner-fixed 3:1 canonical likelihoods. It passes **46/46** deterministic protocol canaries and **157/157** repository tests. Public development result: Raw **0.76875**, Seed **0.98750**, gain **+0.21875**, strict wins **75%**, CI **[+0.06250, +0.46875]**, verifier acceptance **100%**.

The eight-task public suite remains development-only. Candidate commit `2b98491641426f9ebe1678b8491a18a583e6c784` and preregistration commit `393c22abf67e70675870f7f054eed023685cc08b` were CI-green before private inference. Private-v31 official result: Raw **0.78750**, Seed **0.93472**, gain **+0.14722**, strict wins **77.78%**, CI **[+0.01806, +0.28472]**, verifier acceptance **83.33%**. Only the frozen mean-gain >=0.15 check failed. V31P01 also contains a documented Raw-side CUDA/Ollama infrastructure crash that artificially favors Seed in the official score; excluding that pair diagnostically lowers gain to **+0.09706**. Therefore the attempt cannot be promoted under any defensible treatment and the holdout is retired. See [`GATE2_PRIVATE_HOLDOUT_V31_RESULT.md`](GATE2_PRIVATE_HOLDOUT_V31_RESULT.md).

Post-v31 vNext work hardens the campaign boundary before any new freeze: provider/transport and trusted-runner failures are explicit execution incidents, `clean_execution` is mandatory for promotion, trusted mechanical-support defects cannot enter the model-repair path, and bounded task-independent JSON Schemas constrain normal Raw/Seed/verifier Ollama calls. A fixed task-independent provider preflight aborts before scored evidence on provider failure. Schema recovery is capped at **two repair calls total per arm**, shared across stages and verifiers, with qualification proving maximum three-experiment worst cases of Raw **10** and Seed **16** model calls inside the unchanged 16-call envelope. Current validation is **181/181 tests** and **59/59 canaries**. The exact unchanged candidate at source commit `62bf1db71f329abc095d8122214c551f3e1a9cd7` completed a final eight-task public-development run with Raw **0.80000**, Seed **0.98750**, gain **+0.18750**, strict wins **87.5%**, CI **[+0.090625, +0.31875]**, verifier acceptance **100%**, zero repairs, and zero incidents. Every frozen numerical criterion except `valid_pairs >= 16` passes, but this public suite remains non-certifying. The next step is a freeze commit and green CI; only then may a completely fresh private/OOD holdout be created.

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
