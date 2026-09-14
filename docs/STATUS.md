# Implementation Status

Updated: 2026-09-13

Current local validation on Sampath's Windows 11 / Python 3.13.15: **163/163 tests passing** with `ResourceWarning` promoted to an error. The repository includes permanent Ubuntu and Windows CI coverage.

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

**V3.1 private-v31 completed; NOT empirically certified.**

Private v1 remains retired failed evidence: Raw **0.70556**, Seed **0.94167**, gain **+0.23611**, strict wins **66.67%**, CI **[+0.11944, +0.37222]**, verifier acceptance **50%**. Private v2 is also retired: Raw **0.81250**, Seed **0.82083**, gain **+0.00833**, strict wins **33.33%**, CI **[-0.07361, +0.09583]**, verifier acceptance **88.89%**.

V3.1 changes the scientific representation rather than thresholds: one hidden-safe outcome-to-hypothesis attribution call is converted by the trusted runner into fixed 3:1 canonical likelihoods. Experiment choice, posterior updates, Bayes-factor rejection, final hypothesis, and verifier verdicts remain runner-derived.

Deterministic qualification is **46/46 PASS** with implementation digest `c0abee591ed723a46ba57b527c2189efc0d711f3d3a423866a611503e8f16ce8`; repository regression is **157/157 PASS**. On the eight-task public development suite, Raw **0.76875**, Seed **0.98750**, gain **+0.21875**, strict wins **75%**, CI **[+0.06250, +0.46875]**, verifier acceptance **100%**. The public suite is repeatedly observed and cannot certify Gate 2.

The exact v3.1 candidate is frozen at `2b98491641426f9ebe1678b8491a18a583e6c784`; preregistration commit `393c22abf67e70675870f7f054eed023685cc08b` passed GitHub Actions CI #156 before inference. The 18-task private-v31 campaign completed under the frozen candidate/model/envelope. Official score: Raw **0.78750**, Seed **0.93472**, mean gain **+0.14722**, strict wins **14/18 = 77.78%**, paired-bootstrap CI **[+0.01806, +0.28472]**, verifier acceptance **15/18 = 83.33%**. `promotion_pass=false` because mean gain missed the frozen **+0.15000** threshold. A first-call Raw CUDA/Ollama crash on V31P01 is documented as an infrastructure incident; excluding that contaminated pair diagnostically reduces gain to **+0.09706**, so it cannot rescue promotion. The holdout is retired. See [GATE2_PRIVATE_HOLDOUT_V31_RESULT.md](GATE2_PRIVATE_HOLDOUT_V31_RESULT.md).

Post-v31 vNext development now hardens execution integrity: provider/transport failures and trusted-runner failures are explicitly classified as campaign-invalidating incidents, while model/protocol failures and budget exhaustion continue to fail closed at arm level. Current development validation is **163/163 tests PASS**, compileall PASS, and **48/48 Gate-2 canaries PASS** with qualification hash `32227a5665ab34e409eb594b426857760a0f2980fb23a6f30f9daa993e43390a` and implementation digest `685ef4b1c4d31202eac16da1881c96115409965863abd96346175f382a0b5b37`. This is development evidence only; no retired holdout is rerun.

The same post-v31 development line now also uses bounded purpose-specific Ollama JSON Schemas for every normal Gate-2 structured call while leaving repair stage-generic. On the eight-task public development suite: Raw **0.821875**, Seed **0.98750**, gain **+0.165625**, wins **75%**, CI **[+0.06250, +0.303125]**, verifier acceptance **100%**, zero repairs, and zero execution incidents. See [GATE2_VNEXT_STRUCTURED_PUBLIC_RESULT.md](GATE2_VNEXT_STRUCTURED_PUBLIC_RESULT.md).

A task-independent provider-readiness preflight now runs after checkpoint/task identity validation and immediately before the first unfinished scored pair. Its fixed prompt and 8-token output cap are attested in campaign settings; it is outside the Raw/Seed scored envelope, records only prompt/response hashes and token counts on success, hashes failure detail on failure, has no automatic retry, and aborts before scored evidence if the provider cannot respond. A completed resume skips it. At the provider-preflight milestone, development validation was **176/176 tests PASS**, compileall PASS, and **56/56 Gate-2 canaries PASS** with qualification hash `bf52163881fcf6519812cac89e6f0c53361471efe60d1987c79dd679ced57369` and implementation digest `e8b8d4f15aa32babe13dc8640bf9a0df81d82a3ee1066f476757a52aae408785`. A live one-task public smoke confirmed `provider_preflight_passed` precedes `pair_started`; Raw and Seed both succeeded, Seed was accepted, and no repairs or failure classifications occurred.

Schema recovery is now bounded to **two schema-repair calls total per arm**, shared across attribution/action/design/final/verifier stages. Repair attempt #2 may recover a still-invalid first repair, but a third schema repair is never attempted. Verifier repairs use the same shared counter and are recorded in `repair_events`. Qualification proves the worst-case model-call count remains inside the unchanged 16-call envelope even for the maximum three-experiment task: Raw **10**, Seed **16**. Current development validation is **181/181 tests PASS**, compileall PASS, and **59/59 Gate-2 canaries PASS** with qualification hash `7df14fe831d3d1f5b5f247bb3e244080763e955b139c377ed06f4c833dc88fde` and implementation digest `56707e7012af796b21c0304d6f2b3f4a903b95655dee28abd4181cc9a308bdf3`. A public-task fault injection confirmed an initially malformed attribution plus malformed repair #1 can recover on repair #2 and complete the Seed arm with **8 model calls**. This is development evidence only.

See [`GATE2_V31_PUBLIC_RESULT.md`](GATE2_V31_PUBLIC_RESULT.md), [`GATE2_PRIVATE_HOLDOUT_V1_RESULT.md`](GATE2_PRIVATE_HOLDOUT_V1_RESULT.md), and [`GATE2_PRIVATE_HOLDOUT_V2_RESULT.md`](GATE2_PRIVATE_HOLDOUT_V2_RESULT.md).

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

Gate 2 remains uncertified after private v1, v2, and v3.1. Do not rerun or tune on any retired holdout. Post-v31 execution-integrity, structured-output, provider-preflight, and bounded schema-repair hardening are development-only and are evaluated only on public/dev data. Once the new candidate is finalized, freeze it, require green CI, create a completely new external >=16-pair private/OOD holdout after the freeze, preregister it, require preregistration CI, and only then infer.

## Overall

Gate 0 is complete and Gate 1 is **empirically certified**. Gate 2 remains **not certified** after three private attempts; v3.1 was a strong near-miss but failed the frozen mean-gain requirement and is retired evidence. Gates 3-4 remain implemented foundations awaiting later empirical qualification.
