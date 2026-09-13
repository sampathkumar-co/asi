# Gate 2 v3.1 Private Holdout — Preregistration

Date: 2026-09-13

## Purpose

This document preregisters the first private/OOD certification attempt for the frozen Gate-2 v3.1 outcome-attribution candidate. It is written after candidate freeze, successful GitHub Actions CI, private-suite creation, and private task/key audit, but **before any private-v3.1 model inference**.

The public calibration suite and private holdouts v1/v2 are retired evidence. None may be reused as fresh certification data for this attempt.

## Frozen candidate identity

- source commit: `2b98491641426f9ebe1678b8491a18a583e6c784`
- commit message: `Freeze Gate 2 v3.1 attribution candidate`
- Gate-2 implementation digest: `c0abee591ed723a46ba57b527c2189efc0d711f3d3a423866a611503e8f16ce8`
- deterministic Gate-2 qualification: **46/46 PASS**
- qualification content hash: `50a481bfb667505ad95a0050a3fc82218b51a9a6fbadda7d405adc76f4f69799`
- local repository regression: **157/157 PASS** with `ResourceWarning` promoted to an error
- compileall: **PASS**
- Git diff hygiene: **PASS**
- Markdown link audit: **39 files, 0 missing links**
- GitHub Actions: CI run **#155**, run id `34750969236`, conclusion **success**

No candidate source, scorer, verifier policy, protocol, resource limit, likelihood rule, or promotion threshold may change after this preregistration for this holdout attempt.

## Frozen model identity

- provider: local Ollama
- model: `qwen3:8b`
- model manifest SHA-256: `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`
- model artifact size recorded for this digest: `5225388164` bytes
- temperature: `0.0`
- thinking mode: disabled
- context window: `4096`

## Frozen public-development identity

The public suite is **not** certification evidence; these hashes bind the development record used to freeze this candidate.

- public suite id: `gate2-public-calibration-v1`
- task SHA-256: `82099cbd17c63c53d8b08af4f2b1ee561b4f22448af373abffdc68e100939b51`
- answer-key SHA-256: `ea2affbda2d53e478414efab3041290fecc0be403779ceee38541a382e9266a4`
- evidence content hash: `b760625388757dd810785d474e5777cd1fed8d0c89d83790f04df3de4f8273ce`
- evidence file SHA-256: `81e89e8665d382bb73b4d1dc706d6d7626e0cb7ae21b69861cbe3d7f1c70556d`
- score content hash: `b7ab06da04797bbeebe189d9e9dbb19b9e48ac1da1c305c2d37b9df7f4269be6`
- normalized Git score artifact SHA-256: `92f48ef5ce8fdf80c915a3f136a33ee84456ca2a7a4b49a85768e76c9016b43c`
## Frozen private holdout identity

The private files remain outside Git under `AppData/Local/ProjectSeed/gate2-private-holdout-v31`. Only hashes and non-secret audit metadata are committed.

- suite id: `gate2-private-holdout-v31`
- paired task count: **18**
- task-file SHA-256: `408542488bc207f2d7b3f169ca4357e001e3cfded8872249ac17461bdf44f24a`
- answer-key SHA-256: `d7e104467cc80a472d60ba2a3de32c50c224d5c7d1f0c6a7918c1d3433d364f9`
- audit-file SHA-256: `431bc0e63e35a45d9a1db41cbe408cd256959ab54e9fcdb7f09552ed94ce0a14`
- correct-label balance: **H1=6, H2=6, H3=6**
- exact public/private-v1/private-v2 task-id overlap: **0**
- exact public/private-v1/private-v2 question overlap: **0**
- maximum fuzzy question similarity to public/private-v1/private-v2: **0.696078431373**
- pre-inference fuzzy rejection guard: **0.72**; audit result **PASS**
- structural task/key validation: **PASS (18/18)**
- semantic identifiability audit: both hidden E1/E2 observations uniquely match the keyed hypothesis on **18/18** tasks
- all tasks declare `max_experiments=2`
- no private evidence file existed at preregistration preparation time

The private answer key is never supplied to Raw or Seed prompts. Hidden observations remain inaccessible until the trusted runner reveals the selected experiment.

## Common resource envelope

Both Raw and Seed use the same hard per-task envelope:

- maximum steps: **16**
- maximum model calls: **16**
- maximum tool calls: **0**
- maximum accepted tokens: **15,000**
- maximum API cost: **$0**

Normal Seed execution is six model calls: one hidden-safe attribution call, two design/control calls for runner-selected experiments, final explanation, independent verifier, and adversarial verifier. The model does not supply probability magnitudes or override runner-derived experiment selection, posterior, rejection, or final hypothesis.

## Frozen scoring rubric

Per-task score weights remain unchanged:

- correct final hypothesis: **0.40**
- first experiment discriminating: **0.15**
- at least one informative experiment: **0.05**
- pre-evidence prediction consistency: **0.15**
- required controls: **0.10**
- evidence-driven rejection/revision: **0.10**
- critical risk/confound detection: **0.05**

Failed or budget-exhausted arms score zero. Raw and Seed evidence must validate under identical model identity and resource limits.

## Frozen promotion criteria

Gate 2 promotes on this holdout only if **all** of the following hold:

- valid paired tasks >= **16**
- Seed mean >= **0.75**
- mean Seed-minus-Raw gain >= **0.15**
- strict Seed win rate >= **60%**
- deterministic paired-bootstrap lower confidence bound > **0**
- Seed independent+adversarial verifier acceptance >= **75%**
- no identity, integrity, resource-envelope, answer-key, or protocol mismatch

The paired bootstrap is fixed at **4,000 samples** with random seed **0**.

## Execution rule

Private inference may begin only after this preregistration commit is pushed and GitHub Actions is green on the exact preregistration SHA. After the first private model call, the candidate, scorer, thresholds, task file, answer key, verifier policy, canonical 3:1 likelihood rule, and resource envelope are immutable for this attempt.

If the campaign fails, preserve it as failed evidence and do not tune or rerun on this holdout. If an evaluator implementation defect is discovered after inference, stop the certification claim, preserve all sealed evidence, document the incident, and resolve it transparently rather than altering the sealed campaign.