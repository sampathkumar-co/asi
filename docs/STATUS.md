# Implementation Status

Updated: 2026-09-11

Current local validation on Sampath's Windows 11 / Python 3.13.15: **157/157 tests passing** with `ResourceWarning` promoted to an error. The repository includes permanent Ubuntu and Windows CI coverage.

## Meaning of status labels

- **Implemented**: code exists in this repository.
- **Infrastructure-qualified**: deterministic fail-closed qualification passes.
- **Experiment-ready**: real-model protocol, evidence schema, frozen envelope and scoring path are implemented.
- **Empirically tested**: at least one real hidden/OOD campaign has completed under a frozen candidate/model/evaluator identity.
- **Empirically certified**: a real hidden/OOD campaign has passed the gate's preregistered scientific promotion criteria.

## Gate 0 — COMPLETE / infrastructure-qualified

Gate-0 evaluation infrastructure is complete and qualified.

Implemented:
- external private/OOD holdout loader;
- repeated evaluation and confidence summaries;
- paired bootstrap comparison;
- explicit resource accounting;
- content-hashed and signed receipts;
- evaluator-tree integrity snapshots;
- tamper rejection;
- known-good / known-bad fail-closed canaries;
- machine-readable certificate output;
- Windows-safe SQLite/EventStore lifecycle.

Gate 0 qualifies the measurement/control instrument. It does not claim AGI, ASI or recursive amplification.

## Gate 1 — COMPLETE / EMPIRICALLY CERTIFIED

The Gate-1 infrastructure is implemented and empirically certified. Holdout v5 is the first preregistered campaign to satisfy every frozen promotion criterion.

### Implemented foundation

- bounded planner/executor/critic loop;
- persistent memory and event provenance;
- strict JSON planner/critic contracts;
- evidence-only critic and verified-answer gate;
- explicit tool allowlists;
- hard step/model/tool/token/cost budgets;
- budget-metered provider wrapper and transcript hashes;
- raw-model comparison arm;
- local Ollama provider with exact model digest attestation;
- same-model/same-envelope pair evidence;
- deterministic goal-based relevant-tool routing;
- exact tools for shortest paths, DAG critical paths, CRT, semantic transactions/reconciliation, generic aggregation, finite/assignment CSP, exact Python tracing and constrained subset optimization;
- sandboxed `python_compute` fallback;
- per-task checkpoint/resume and progress telemetry;
- Seed implementation digest attestation;
- external answer-key scoring and paired bootstrap;
- rejection of mixed model/envelope/implementation evidence;
- real ChatGPT pilot protocol retained as a separate pilot path.

### Development/calibration campaign

The first 8-task Qwen3-8B calibration campaign produced:
- Raw: **2/8 = 25%**;
- Seed: **4/8 = 50%**;
- observed gain: **+25 percentage points**;
- strict Seed win rate: **50%**;
- 95% paired-bootstrap CI crossed zero.

That suite was then treated only as development data. It was not reused as certification evidence after architecture changes.

### Preregistered unseen holdout v2

Candidate source commit: `8c18f91ad72c31007243e4bf2b8388b1421efd00`.

Preregistration commit: `8f38b01604964b1e6aabbef10d842051c52fb25c`.

Model: local `qwen3:8b`, digest `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`.

The 16-task private holdout was independently audited before model inference; all exact-answer tasks and relevant optimum/path/assignment solutions were reproduced and uniqueness-checked. Task and answer-key contents remain outside source control.

Final corrected score:
- Raw: **1/16 = 6.25%**;
- Seed: **5/16 = 31.25%**;
- observed mean gain: **+25 percentage points**;
- strict Seed win rate: **31.25%**;
- 95% paired-bootstrap CI: **[0.00, 0.50]**.

Frozen promotion thresholds required >=16 valid pairs, >=5 percentage-point gain, >=60% strict Seed win rate and CI lower bound >0. Pair count and mean gain passed. Win rate and CI did not. **At that point Gate 1 remained NOT EMPIRICALLY CERTIFIED.**

Full result: [`GATE1_LOCAL_HOLDOUT_V2_RESULT.md`](GATE1_LOCAL_HOLDOUT_V2_RESULT.md). Public score-only artifact: [`../artifacts/gate1-local-holdout-v2-score.json`](../artifacts/gate1-local-holdout-v2-score.json).

### Scoring correction

After the 16-pair run had fully completed, the first score attempt exposed two evaluator-side parsing bugs: single-string answer keys were iterated character-by-character, and `FINAL:` prefixes in keys were not normalized like model outputs. The frozen task/key/evidence artifacts and Seed/model run were not changed. Both bugs were fixed with regression tests, after which the repository passed **121/121 tests** and the same sealed evidence/key hashes produced the result above.

### Gate-1 vNext development candidate

Post-v2 development is frozen at source commit `83ec193d6300b0658af8d4d3c45109880b28363f`, implementation digest `a82be2b8cd2a60e4fa4021a0d6bfa0434c73032afbf0ec29771626385dccd708`. The candidate passes **131/131** local tests and **10/10** deterministic Gate-1 infrastructure canaries.

Retired-holdout development probes verify the intended generic fixes for critical-path finalization, transaction/reconciliation semantics, ordering-format fidelity, exact Python tracing and structured subset optimization. These probes are development evidence only. See [`GATE1_VNEXT_DEVELOPMENT.md`](GATE1_VNEXT_DEVELOPMENT.md).

### Preregistered unseen holdout v3

Frozen vNext source: `83ec193d6300b0658af8d4d3c45109880b28363f`; implementation digest: `a82be2b8cd2a60e4fa4021a0d6bfa0434c73032afbf0ec29771626385dccd708`; preregistration commit: `f10457f41d167551657e7e0e2b7741f79ed25b7b`.

Final score: Raw **3/16 = 18.75%**, Seed **11/16 = 68.75%**, mean gain **+50 pp**, strict Seed win rate **56.25%**, 95% paired-bootstrap CI **[+18.75 pp, +81.25 pp]**. Pair count, gain, CI, identity/integrity, and resource criteria passed. The frozen >=60% strict-win criterion failed, so **at that point Gate 1 remained NOT EMPIRICALLY CERTIFIED**.

Full audit: [`GATE1_LOCAL_HOLDOUT_V3_RESULT.md`](GATE1_LOCAL_HOLDOUT_V3_RESULT.md).

### Gate-1 v4 certification campaign

Frozen source: `b4242af758b1222f8ecea0bf7306e917a36ed9d8`; implementation digest: `f9d882e185b235d0a8345640ee1577edb518be96dbf8af0f6b50ec204f5a1358`; preregistration commit: `e346ffabb2f77bded32d29e58e8009dc2731fd20`.

The private v4 holdout was generated after candidate freeze, independently audited **16/16**, and scored only after all 16 pairs sealed. Final score: Raw **3/16 = 18.75%**, Seed **11/16 = 68.75%**, mean gain **+50 pp**, strict Seed win rate **8/16 = 50.00%**, 95% paired-bootstrap CI **[+25.00 pp, +75.00 pp]**.

Pair count, gain, CI, identity/integrity and resource criteria passed. The frozen >=60% strict-win criterion failed, so **at that point Gate 1 remained NOT EMPIRICALLY CERTIFIED**. Full audit: [`GATE1_LOCAL_HOLDOUT_V4_RESULT.md`](GATE1_LOCAL_HOLDOUT_V4_RESULT.md).

The evaluated v4 candidate remains green at **134/134** local tests and **10/10** deterministic Gate-1 checks after the run.

### Gate-1 v5 promotion campaign — PASS

Frozen source: `c34e1cd31c61efebc513f289ba9ac11cdd4412d0`; implementation digest: `011881547d85a31cccc3bd66a174e7ae9b3e8506014a6c918d248e78708e286c`; preregistration: `857aa0f4cac7437deb86646e6f72d682b16d806a`.

The new private holdout was independently audited **16/16** before inference. Final score: Raw **1/16 = 6.25%**, Seed **15/16 = 93.75%**, mean gain **+87.50 pp**, strict Seed win rate **14/16 = 87.50%**, 95% paired-bootstrap CI **[+68.75 pp, +100.00 pp]**. Identity/integrity and resource-envelope audits passed. **Gate 1 promotes.**

Full audit: [`GATE1_LOCAL_HOLDOUT_V5_RESULT.md`](GATE1_LOCAL_HOLDOUT_V5_RESULT.md). Public score-only artifact: [`../artifacts/gate1-local-holdout-v5-score.json`](../artifacts/gate1-local-holdout-v5-score.json).

## Gate 2 — scientific-method workflow

**Development candidate frozen; public calibration complete; private/OOD certification pending.**

Current candidate:
- 28/28 deterministic Gate-2 protocol canaries pass;
- 157/157 repository tests pass under `ResourceWarning`-as-error;
- implementation digest `49c9db731136a98c0bef78627fd3952d5e2b9b1b1030eb8e6dbc7c5d4647ea7a`;
- same local `qwen3:8b` artifact for Raw/Seed, 16 calls / 16 steps / 12,000 tokens / zero tools;
- isolated blind per-hypothesis forecasts, optional two-way first-experiment collision audit, reveal-then-mechanical comparison, explicit revision, bounded repair, and independent/adversarial verification.

Final eight-task public development result: Raw **0.78750**, Seed **0.93125**, gain **+0.14375**, strict Seed wins **5/8 = 62.5%**, verifier acceptance **6/8 = 75%**, bootstrap CI **[-0.015625, +0.31875]**. This does **not** certify Gate 2: it has only 8 pairs, mean gain is below the frozen +0.15 threshold, and the CI lower bound is not positive.

The public suite is retired as development evidence. Next: freeze the candidate in Git/CI, generate and independently audit a new >=16-pair external private/OOD holdout, preregister hashes and frozen criteria, then run inference once.

## Gate 3 — architecture search

**Implemented + tested bounded search; not empirically certified.**

Implemented:
- declarative architecture genome;
- seeded bounded mutations;
- archive/deduplication;
- capability/cost fitness;
- multi-generation search.

## Gate 4 — controlled self-modification

**Implemented + tested control foundation; not empirically certified.**

Implemented:
- structured source mutation proposal;
- mutation allow/deny paths;
- byte/file budgets;
- stale-write hash checks;
- copy-on-write descendants;
- Docker no-network/read-only command;
- promotion evidence gate;
- durable lineage store.

## Current execution/storage policy

- canonical Project Seed state stays in `sampathkumar-co/asi` on GitHub;
- Sampath's laptop is the active local validation machine at `C:\Users\SAMPATH\OneDrive\Desktop\asi`;
- the local clone tracks GitHub `main` and should remain clean except ignored runtime artifacts;
- private holdout tasks, answer keys and raw evidence stay under the external control-plane directory and are not committed;
- GitHub contains only code, documentation, hashes and sanitized score artifacts;
- GitHub Actions remains the independent clean CI environment;
- Yaswanth's machine is not used for active Seed state while Sampath is online.

## Current next step

Gate 1 is complete. The active empirical milestone is **Gate 2 private/OOD certification**: commit and CI-freeze the current candidate, create and independently audit a new external >=16-pair holdout, preregister hashes/identity/budgets/rubric/thresholds, then run the sealed paired campaign without post-inference tuning.

## Overall

Gate 0 is complete and Gate 1 is **empirically certified**. Gate 2 has a frozen development candidate with strong but non-promoting public calibration evidence; empirical certification still depends on a new preregistered private/OOD >=16-pair campaign. Gates 3-4 remain implemented foundations awaiting later empirical qualification.
