# Gate 2 Development Record

Updated: 2026-09-13

## Scope

This document records Gate-2 **development evidence**. It is intentionally separate from private certification evidence. The public calibration suite has been observed repeatedly during protocol development and is therefore retired for certification purposes.

## Public calibration suite

Suite: `gate2-public-calibration-v1`

Eight synthetic scientific-method tasks cover:

- selection confounding;
- cache/warm-up effects;
- train/test contamination;
- sensor drift;
- subgroup imbalance;
- workload change;
- retrieval leakage;
- random-seed variance.

Final public task SHA-256: `82099cbd17c63c53d8b08af4f2b1ee561b4f22448af373abffdc68e100939b51`.

Final public development answer-key SHA-256: `ea2affbda2d53e478414efab3041290fecc0be403779ceee38541a382e9266a4`.

The public key exists only for development calibration and must never be supplied to candidate prompts.

## Development sequence

Early Gate-2 versions exposed several real protocol defects rather than being declared successful:

1. no explicit post-reveal revision stage;
2. ambiguous selected-hypothesis prediction semantics;
3. all-hypothesis forecast matrices that Qwen could invert causally;
4. an 8k token budget too small for the expanded scientific loop;
5. schema failures whose rejected model responses were not sufficiently auditable;6. verifier outputs whose labels contradicted their own explanations;
7. a global experiment-planning call that was unstable on workload-confound tasks;
8. collision resolution that became harmful when three hypotheses were all ambiguous.

Each of those failures was retained as development evidence. Promotion thresholds were not weakened.

## Final development candidate

The frozen pre-commit implementation digest is:

`49c9db731136a98c0bef78627fd3952d5e2b9b1b1030eb8e6dbc7c5d4647ea7a`

The deterministic Gate-2 qualification currently passes **28/28** canaries. Qualification content hash:

`b02ef57a4c1bd48cdc57f3b5905f421e7fbcb6d9f652e94ba86e46d9aba9597e`

Repository regression at freeze point: **157/157 tests passing** with `ResourceWarning` promoted to an error, plus a clean `compileall` pass.

The final candidate uses:

- falsifiable Seed action selection;
- one blind forecast call per hypothesis;
- optional first-experiment collision audit only for exactly two colliding hypotheses;
- mechanical forecast-vs-observation comparison after reveal;
- explicit post-reveal revision;
- independent and adversarial verifier calls;
- runner-derived verifier verdicts;
- explicit bounded repair;
- transcript-audited post-response budget rejection.

A proposed global first-experiment planner was tested and **retired** because it caused a workload-confound regression. It is not part of the frozen candidate.

## Final public calibration

Evidence content hash:
`c804faac5ebe4ffa837c4cd43f68e7f86a0bb9516d89b7dfbbb7a6cc032fe772`.

Evidence-file SHA-256:
`fb049178bde739d12bf1c85dc581a1ec11edb3f83450570471bd91f3b865c8f6`.

Score content hash:
`f176cfd61256f647faa53378b75594fab2ff077fd538d2babd7058485bc15418`.
Final eight-pair public result:

- Raw mean: **0.78750**;
- Seed mean: **0.93125**;
- mean gain: **+0.14375**;
- strict Seed win rate: **5/8 = 62.5%**;
- paired-bootstrap CI: **[-0.015625, +0.31875]**;
- Seed verifier acceptance: **6/8 = 75%**;
- all eight Seed arms completed successfully and selected the correct final H2;
- no repair or budget-exhaustion failure occurred.

The public run passes Seed mean, strict-win, and verifier-acceptance checks. It misses the frozen mean-gain threshold by **0.00625**, the CI lower bound remains slightly below zero, and the suite has only 8 pairs versus the required 16.

**This is not a Gate-2 promotion result.**

## Why development stops here

The same eight public tasks have been inspected repeatedly while fixing protocol defects. Continuing to tune specifically against their remaining score gaps would increasingly measure adaptation to known calibration tasks rather than general scientific-method improvement.

Therefore this candidate is frozen for an untouched >=16-pair private/OOD campaign. The private campaign, not another pass over these eight known tasks, will decide empirical certification.

No private task, answer key, or hidden outcome was used to choose the final candidate.
## Post-freeze private holdout v1 result

The frozen source commit `ec1e98315a0baa2fe47d344702790b86bbc6132f` and preregistration commit `2126f64b7d37964edf019794507cd19d021f2fd8` both passed CI before private inference.

On 18 balanced private/OOD tasks, Raw mean was **0.70556** and Seed mean **0.94167**, producing **+0.23611** mean gain. Strict Seed wins were **66.67%** and the 4,000-sample paired-bootstrap interval was **[+0.11944, +0.37222]**.

Seed verifier acceptance was **9/18 = 50%**, below the preregistered **75%** threshold. Therefore the private run does not promote Gate 2 even though all score-based transfer checks pass.

This holdout is now retired. The next development cycle may study its verifier failures, but no changed candidate may claim certification on these same 18 tasks. A later certification attempt requires a completely new independently audited and preregistered private/OOD holdout.

See [`GATE2_PRIVATE_HOLDOUT_V1_RESULT.md`](GATE2_PRIVATE_HOLDOUT_V1_RESULT.md).

## Gate-2 v2 verifier/research development

Private v1 failed only the verifier-acceptance criterion. Diagnostic review showed that eight correct Seed conclusions were rejected largely because model verifiers converted generic residual uncertainty into hard defects. The v2 cycle therefore changed verifier semantics without weakening any promotion threshold.

Several categorical forecast-rescue designs were tested and rejected during development: global planning, collision audits, anchored collision refinement, and all-tie experiment fallback. Stress tests showed that categorical collision prompts could hallucinate distinctions or mutate otherwise-correct forecasts. Those rescue paths are **not** part of v2.

The v2 candidate instead records one blind **probability distribution over declared outcomes per hypothesis per experiment before reveal**. The runner derives categorical argmax predictions for the unchanged scoring rubric, while trusted verifier support is the cumulative product of the frozen probability assigned to each observed outcome. Exact ties remain failures rather than being forced apart.

Verifier model outputs are also structured: they name every declared hypothesis tied for strongest support and flag only concrete direct evidence/protocol defects. The runner accepts a verifier only when the final hypothesis is the unique mechanical likelihood winner, the verifier supports only that hypothesis, and no direct defect exists.

Current pre-commit v2 implementation digest:
`d8a028f394121ca3dc6e5c890304bd3d13cd03e5566467befecb31190540b340`.

Deterministic qualification: **36/36** canaries. Repository regression: **157/157** tests with `ResourceWarning` promoted to an error, plus clean `compileall` and `git diff --check`.

Common Raw/Seed envelope: **16 steps / 16 model calls / 0 tools / 15,000 tokens / $0**. Model remains local `qwen3:8b` digest `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`.

### v2 public development result

Fresh eight-pair evidence content hash: `5db6f27ff34fe0138a2f499361960ac63b32faa4b9d56fa1a2bd355a97a5197a`.
Evidence-file SHA-256: `13258ebf0a6bc405a2683cf98f4531fdb8e929f026b2319efab54562e448782f`.
Score content hash: `15cc46330eb28a212ca91a045ba12ba86c066c80a3217ac620e567b0f742629f`.

Raw mean **0.75625**; Seed mean **0.94375**; mean gain **+0.18750**; strict Seed wins **6/8 = 75%**; paired-bootstrap CI **[+0.025, +0.35]**; Seed verifier acceptance **8/8 = 100%**. Every Seed arm succeeded with final H2, unique mechanical likelihood support for H2, zero repairs, and no budget failure.

This development run passes every frozen numerical criterion except `valid_pairs >= 16`, which cannot be satisfied by the eight-task public suite by construction. It is **not** certification evidence. The public suite has been repeatedly observed and remains retired for certification.

### v2 private certification result

Frozen candidate `261cc0d486830b3219a58d499661ccf1c7f1327b` and preregistration `f7a461881e691640f0a822548bd39de473ef2536` both passed CI before inference. On 18 balanced private/OOD pairs, Raw mean was **0.81250** and Seed mean **0.82083**, for only **+0.00833** mean gain. Strict Seed wins were **33.33%**, bootstrap CI **[-0.07361, +0.09583]**, and verifier acceptance **88.89%**.

Thus v2 fixed the dominant v1 verifier false-negative failure but did not demonstrate the preregistered incremental capability gain. Mean gain, strict-win rate, and positive-CI checks failed; Gate 2 remains uncertified. Private v2 is permanently retired. See [`GATE2_PRIVATE_HOLDOUT_V2_RESULT.md`](GATE2_PRIVATE_HOLDOUT_V2_RESULT.md).

At that point, the next legitimate development cycle was **v3**, focused on actual Raw-to-Seed capability gain rather than further verifier-threshold tuning. Private v1/v2 may be used only diagnostically. Any new certification attempt requires a new frozen candidate and a completely new audited/preregistered private/OOD holdout.

## Gate-2 v3 and v3.1 development

V3 moved experiment selection, posterior updates, Bayes-factor rejection, and final hypothesis choice into the trusted runner, but its independent per-hypothesis probability forecasts were not cross-hypothesis calibrated. On a fresh eight-task public run, v3 scored Raw **0.821875**, Seed **0.59375**, gain **-0.228125**, strict wins **12.5%**, CI **[-0.484375, +0.059375]**, verifier acceptance **62.5%**. Forecast-signature collisions and arbitrary confidence magnitudes caused the regression. V3 is failed development evidence and is not a certification candidate.

V3.1 reverses the forecasting direction. One pre-reveal call attributes each possible outcome to the declared hypothesis/hypotheses that would naturally cause it. Across the repeatedly observed public suite, the diagnostic attribution probe recovered **48/48** E1/E2 development-key relations exactly. The runner then uses a task-independent fixed **3:1** support likelihood ratio; the model no longer emits probability magnitudes.

The resulting candidate passes **46/46** deterministic qualification canaries, **157/157** repository tests, compileall, and diff hygiene. Implementation digest: `c0abee591ed723a46ba57b527c2189efc0d711f3d3a423866a611503e8f16ce8`.

Fresh v3.1 public-development evidence hash: `b760625388757dd810785d474e5777cd1fed8d0c89d83790f04df3de4f8273ce`. Score: Raw **0.76875**, Seed **0.98750**, gain **+0.21875**, strict wins **75%**, CI **[+0.06250, +0.46875]**, verifier acceptance **100%**. All eight Seed arms succeeded with six calls and zero repairs. See [`GATE2_V31_PUBLIC_RESULT.md`](GATE2_V31_PUBLIC_RESULT.md).

The public suite and retired private v1/v2 evidence were used diagnostically during development. V3.1 was then frozen and evaluated exactly once on `gate2-private-holdout-v31`; that attempt did not promote because mean gain was **+0.14722 < +0.15000**, and the holdout is permanently retired. See [`GATE2_PRIVATE_HOLDOUT_V31_RESULT.md`](GATE2_PRIVATE_HOLDOUT_V31_RESULT.md).

## Post-v31 vNext execution-integrity hardening

The first post-v31 change addresses the infrastructure incident observed on `V31P01_CORROSION`. Provider/transport failures are now represented separately from model/protocol failures. `provider` and trusted-`runner` failures are recorded as execution incidents and force `clean_execution=false`, making the whole campaign non-promotable rather than silently converting an infrastructure failure into a score-like zero. Budget exhaustion and malformed model output remain ordinary fail-closed arm outcomes.

The runner also separates trusted mechanical-support failures from repairable model-output validation. A trusted-runner consistency defect can no longer be caught by the model schema-repair path and repaired away. Failure telemetry records a bounded classification/message while the scorer exposes only a hash of infrastructure-failure detail in sanitized incident summaries.

Current post-v31 development-tree validation is **163/163 tests PASS**, compileall PASS, and **48/48 Gate-2 deterministic canaries PASS**. Qualification hash: `32227a5665ab34e409eb594b426857760a0f2980fb23a6f30f9daa993e43390a`. Development implementation digest: `685ef4b1c4d31202eac16da1881c96115409965863abd96346175f382a0b5b37`. This is infrastructure hardening only; it is **not** a new empirical certification candidate and does not authorize reuse of any retired holdout.

## Post-v31 vNext structured-output hardening

The next generic reliability change adds purpose-specific Ollama JSON Schemas for Raw actions, Seed attribution/design, final reports, and both verifiers while leaving stage-dependent repair generic. Dynamic scientific IDs remain runner-validated, and the schemas contain no task-specific or private-answer identities. The development tree now passes **168/168 tests** and **54/54 Gate-2 canaries**, qualification hash `71401491db4d22ec3111c5e109319cb623ad4ed8f9f51c5942675842dfee18d2`, implementation digest `56d144466987e62295830dc3335fda4dde1ebafb4dfb4a6d65563cc92f25bb82`.

On the full eight-task public-development suite, all 8 pairs sealed with zero repairs and zero execution incidents. Raw **0.821875**, Seed **0.98750**, gain **+0.165625**, strict wins **75%**, CI **[+0.06250, +0.303125]**, verifier acceptance **100%**. Seed is unchanged task-for-task versus frozen v3.1 public development; the reduced gain comes from Raw `CAL01_SELECTION` improving from 0 to 0.425. See [`GATE2_VNEXT_STRUCTURED_PUBLIC_RESULT.md`](GATE2_VNEXT_STRUCTURED_PUBLIC_RESULT.md).
