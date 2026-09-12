# Gate 2 Private Holdout v2 — Preregistration

Date: 2026-09-12

## Purpose

This document preregisters the second private/OOD empirical certification attempt for Project Seed Gate 2. It is written **after the probabilistic v2 candidate was frozen and CI-green, and after the new private suite was independently audited, but before any private-v2 model inference**.

The eight-task public calibration suite and private holdout v1 are retired evidence. Neither may be reused as fresh certification data for this candidate.

## Frozen candidate identity

- source commit: `261cc0d486830b3219a58d499661ccf1c7f1327b`
- commit message: `Freeze Gate 2 probabilistic verifier candidate`
- Gate-2 implementation digest: `d8a028f394121ca3dc6e5c890304bd3d13cd03e5566467befecb31190540b340`
- deterministic Gate-2 qualification: **36/36 PASS**
- qualification content hash: `6813ecbd9edd4324c0a027677a98546add1921e1a62745580190c338f2d9ab9e`
- local repository regression: **157/157 PASS** with `ResourceWarning` promoted to an error
- GitHub Actions: CI run **#152**, run id `34684793621`, conclusion **success**

No candidate source, scorer, verifier policy, protocol, resource limit, or promotion threshold may change after this preregistration for this holdout attempt.

## Frozen model identity

- provider: local Ollama
- model: `qwen3:8b`
- model manifest SHA-256: `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`
- model size recorded during development: `5225388164` bytes
- temperature: `0.0`
- thinking mode: disabled
- context window: `4096`

## Frozen private holdout identity

The private files remain outside Git under `AppData/Local/ProjectSeed/gate2-private-holdout-v2`. Only hashes and non-secret audit metadata are committed.

- suite id: `gate2-private-holdout-v2`
- paired task count: **18**
- task-file SHA-256: `98432c2baf6be32ed5a6245458f61e54655e2afe46dd82be066306adf0f453e0`
- answer-key SHA-256: `0201a17e96606c203f0bb464ea098cbb2216fb22025e370bcfa4f293c4c239b5`
- audit SHA-256: `4ee584610f368e87ac4fcd65f511204e650359c3c7428c6b8d11ab8bc0b8206f`
- correct-label balance: **H1=6, H2=6, H3=6**
- exact public/private-v1 task-id overlap: **0**
- exact public/private-v1 question overlap: **0**
- maximum fuzzy question similarity to public/private-v1: **0.6108**, below the pre-inference **0.72** rejection guard
- structural task/key validation: **PASS (18/18)**
- semantic identifiability audit: hidden E1 and E2 outcomes uniquely match the keyed hypothesis on **18/18** tasks

The private answer key is never supplied to Raw or Seed prompts. Hidden observations remain inaccessible until the trusted runner reveals the selected experiment.

## Common resource envelope

Both Raw and Seed use the same hard per-task envelope:

- maximum steps: **16**
- maximum model calls: **16**
- maximum tool calls: **0**
- maximum accepted tokens: **15,000**
- maximum API cost: **$0**

A response that returns after exceeding the token budget remains transcript-audited with `budget_accepted=false` and is not accepted into the arm state.

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

- at least **16 valid paired tasks**
- Seed mean score **>= 0.75**
- mean Seed-minus-Raw gain **>= 0.15**
- strict paired Seed win rate **>= 60%**
- paired-bootstrap 95% CI lower bound **> 0**
- Seed independent+adversarial acceptance **>= 75%**
- no identity, integrity, resource-envelope, checkpoint, protocol, or answer-key-separation failure

The paired bootstrap remains frozen at **4,000 samples, seed 0**.

## Frozen execution discipline

1. Commit and push this preregistration separately from the candidate source, then require clean GitHub CI before private-v2 inference begins.
2. Immediately before the first private model call, re-hash the candidate implementation, Ollama model manifest, task file, answer key, and audit report.
3. Run one paired Raw-vs-Seed campaign using the frozen task file and exact model. Resume is allowed only from a checkpoint accepted by the runner's full identity checks.
4. Do not inspect or use the answer key during candidate execution, and do not change tasks, observations, scorer, thresholds, prompts, protocol, verifier policy, or resource limits after inference begins.
5. Seal all 18 task pairs before the scorer receives the private answer key.
6. Publish only hashes, aggregate/per-task numeric scores, protocol metadata, and non-secret audit results. Keep private task/key contents and raw evidence outside Git.
7. If any frozen criterion fails, Gate 2 remains uncertified; this v2 holdout becomes retired evidence and cannot be reused as fresh certification data after candidate changes.

## Interpretation boundary

A pass would certify this bounded Gate-2 probabilistic scientific-method scaffold on one preregistered private/OOD campaign for the frozen Qwen3-8B substrate. It would **not** by itself establish AGI, ASI, autonomous recursive self-improvement, or sustained recursive amplification.

A failure would remain valid empirical evidence and would not be repaired by changing thresholds or rerunning the same holdout after tuning.

## Pre-inference checklist

- [x] v2 candidate source committed and pushed
- [x] candidate CI green
- [x] brand-new private-v2 tasks and key created outside Git
- [x] structural task/key validation passed
- [x] semantic identifiability audit passed
- [x] fuzzy-overlap guard passed against public and retired private-v1 tasks
- [x] candidate/model/task/key/audit hashes recorded above
- [ ] preregistration commit pushed and CI green
- [ ] private-v2 inference started
