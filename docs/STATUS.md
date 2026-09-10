# Implementation Status

Updated: 2026-09-10

Current local validation on Sampath's Windows 11 / Python 3.13.15: **131/131 tests passing**. The repository includes permanent Ubuntu and Windows CI coverage for the Gate-0/1 foundations.

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

## Gate 1 — EMPIRICALLY TESTED / NOT CERTIFIED

The Gate-1 infrastructure is implemented and has now been exercised in multiple real-model campaigns. The current empirical verdict is **not promoted**.

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

Frozen promotion thresholds required >=16 valid pairs, >=5 percentage-point gain, >=60% strict Seed win rate and CI lower bound >0. Pair count and mean gain passed. Win rate and CI did not. **Gate 1 therefore remains NOT EMPIRICALLY CERTIFIED.**

Full result: [`GATE1_LOCAL_HOLDOUT_V2_RESULT.md`](GATE1_LOCAL_HOLDOUT_V2_RESULT.md). Public score-only artifact: [`../artifacts/gate1-local-holdout-v2-score.json`](../artifacts/gate1-local-holdout-v2-score.json).

### Scoring correction

After the 16-pair run had fully completed, the first score attempt exposed two evaluator-side parsing bugs: single-string answer keys were iterated character-by-character, and `FINAL:` prefixes in keys were not normalized like model outputs. The frozen task/key/evidence artifacts and Seed/model run were not changed. Both bugs were fixed with regression tests, after which the repository passed **121/121 tests** and the same sealed evidence/key hashes produced the result above.

### Gate-1 vNext development candidate

Post-v2 development is frozen at source commit `83ec193d6300b0658af8d4d3c45109880b28363f`, implementation digest `a82be2b8cd2a60e4fa4021a0d6bfa0434c73032afbf0ec29771626385dccd708`. The candidate passes **131/131** local tests and **10/10** deterministic Gate-1 infrastructure canaries.

Retired-holdout development probes verify the intended generic fixes for critical-path finalization, transaction/reconciliation semantics, ordering-format fidelity, exact Python tracing and structured subset optimization. These probes are development evidence only. See [`GATE1_VNEXT_DEVELOPMENT.md`](GATE1_VNEXT_DEVELOPMENT.md).

### Preregistered unseen holdout v3

Frozen vNext source: `83ec193d6300b0658af8d4d3c45109880b28363f`; implementation digest: `a82be2b8cd2a60e4fa4021a0d6bfa0434c73032afbf0ec29771626385dccd708`; preregistration commit: `f10457f41d167551657e7e0e2b7741f79ed25b7b`.

Final score: Raw **3/16 = 18.75%**, Seed **11/16 = 68.75%**, mean gain **+50 pp**, strict Seed win rate **56.25%**, 95% paired-bootstrap CI **[+18.75 pp, +81.25 pp]**. Pair count, gain, CI, identity/integrity, and resource criteria passed. The frozen >=60% strict-win criterion failed, so **Gate 1 remains NOT EMPIRICALLY CERTIFIED**.

Full audit: [`GATE1_LOCAL_HOLDOUT_V3_RESULT.md`](GATE1_LOCAL_HOLDOUT_V3_RESULT.md).

### Gate-1 v4 certification campaign

Frozen source: `b4242af758b1222f8ecea0bf7306e917a36ed9d8`; implementation digest: `f9d882e185b235d0a8345640ee1577edb518be96dbf8af0f6b50ec204f5a1358`; preregistration commit: `e346ffabb2f77bded32d29e58e8009dc2731fd20`.

The private v4 holdout was generated after candidate freeze, independently audited **16/16**, and scored only after all 16 pairs sealed. Final score: Raw **3/16 = 18.75%**, Seed **11/16 = 68.75%**, mean gain **+50 pp**, strict Seed win rate **8/16 = 50.00%**, 95% paired-bootstrap CI **[+25.00 pp, +75.00 pp]**.

Pair count, gain, CI, identity/integrity and resource criteria passed. The frozen >=60% strict-win criterion failed, so **Gate 1 remains NOT EMPIRICALLY CERTIFIED**. Full audit: [`GATE1_LOCAL_HOLDOUT_V4_RESULT.md`](GATE1_LOCAL_HOLDOUT_V4_RESULT.md).

The evaluated v4 candidate remains green at **134/134** local tests and **10/10** deterministic Gate-1 checks after the run.

### Gate-1 v5 development candidate

v5 is frozen at source commit `c34e1cd31c61efebc513f289ba9ac11cdd4412d0`, implementation digest `011881547d85a31cccc3bd66a174e7ae9b3e8506014a6c918d248e78708e286c`. It passes **140/140** local tests and **10/10** deterministic Gate-1 checks. Retired-v4 probes close W401/W403/W404/W412/W413 through generic routing, exact-tool preference, duration-label normalization, exact Python tracing and output canonicalization. See [`GATE1_V5_DEVELOPMENT.md`](GATE1_V5_DEVELOPMENT.md).

## Gate 2 — scientific-method workflow

**Implemented + tested protocol; not empirically certified.**

Implemented:
- hypotheses and falsifiers;
- experiment plans, predictions, metrics and controls;
- reproducibility flag;
- independent + adversarial verification;
- dual-verifier acceptance rule.

Gate-2 empirical work should not begin as a promotion claim until Gate 1 has a qualifying baseline result.

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

## Current Gate-1 next step

Holdouts v2, v3 and v4 are retired development evidence and may not be reused for certification. The v5 candidate is now frozen and locally qualified. The next action is to generate, independently audit and preregister a **new private holdout v5** against that frozen identity, then run the same-model Raw-vs-Seed campaign without architecture changes.

## Overall

Gate 0 is complete. Gate 1 is **infrastructure-qualified, repeatedly empirically tested, and now at a frozen v5 candidate awaiting a fresh holdout, but not empirically certified**. v3/v4 both showed Seed 68.75% vs Raw 18.75% (+50 pp) with CIs above zero, while strict paired reliability remained below 60%. Gates 2-4 remain foundations awaiting later empirical qualification.
