# Gate 2 Private Holdout v1 — Preregistration

Date: 2026-09-11

## Purpose

This document preregisters the first private/OOD empirical certification attempt for Project Seed Gate 2. It is written **after candidate freeze and private-suite audit, but before any private holdout model inference**.

The eight-task public calibration suite is retired development evidence and must not be treated as certification data.

## Frozen candidate identity

- source commit: `ec1e98315a0baa2fe47d344702790b86bbc6132f`
- commit message: `Freeze Gate 2 scientific-method candidate`
- Gate-2 implementation digest: `49c9db731136a98c0bef78627fd3952d5e2b9b1b1030eb8e6dbc7c5d4647ea7a`
- deterministic Gate-2 qualification: **28/28 PASS**
- qualification content hash: `b02ef57a4c1bd48cdc57f3b5905f421e7fbcb6d9f652e94ba86e46d9aba9597e`
- local repository regression: **157/157 PASS** with `ResourceWarning` promoted to an error
- GitHub Actions: CI run **#149**, run id `34622400445`, conclusion **success**

No candidate source, scorer, protocol, resource limit, or threshold may change after this preregistration for this holdout attempt.

## Frozen model identity

- provider: local Ollama
- model: `qwen3:8b`
- model digest: `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`
- model size recorded during development: `5225388164` bytes
- temperature: `0.0`
- thinking mode: disabled
- context window: `4096`
## Frozen private holdout identity

The private files remain outside the Git repository under the external control-plane directory. Only hashes and audit metadata are committed.

- suite id: `gate2-private-holdout-v1`
- paired task count: **18**
- task-file SHA-256: `783007f2eb64df009d359f1ee853e084d244a9a6d34adfbe963c6bdee2c1c146`
- answer-key SHA-256: `43b38aa2728649e17fe9fc5fdfeb4d1695b34bd29972f4506d146ae3092b24a8`
- independent audit SHA-256: `72500f029a9a456cdfad4d81b0cc55d65d13b434e7077fe8ff7f401713e13a20`
- correct-label balance: **H1=6, H2=6, H3=6**
- exact public task-id overlap: **0**
- exact public question overlap: **0**
- structural key validation: **PASS**
- semantic identifiability audit: for every task, the hidden E1 and E2 observations match the keyed final hypothesis prediction and do not match either competing hypothesis prediction

The answer key is never supplied to Raw or Seed prompts. Hidden observed outcomes remain inaccessible until the selected experiment is revealed through the trusted runner.

## Common resource envelope

Both Raw and Seed use the same hard campaign envelope per task:

- maximum steps: **16**
- maximum model calls: **16**
- maximum tool calls: **0**
- maximum accepted tokens: **12,000**
- maximum API cost: **$0**

A response that returns after exceeding the token budget is transcript-audited with `budget_accepted=false` and remains terminal; it does not become accepted usage.
## Frozen scoring rubric

Per-task score weights are frozen as:

- correct final hypothesis: **0.40**
- first experiment discriminating: **0.15**
- at least one informative experiment: **0.05**
- pre-evidence prediction consistency: **0.15**
- required controls: **0.10**
- evidence-driven rejection/revision: **0.10**
- critical risk/confound detection: **0.05**

Failed or budget-exhausted arms score zero for that task. Raw and Seed evidence must validate under identical provider/model identity and resource limits.

## Frozen promotion criteria

Gate 2 promotes on this holdout only if **all** of the following hold:

- at least **16 valid paired tasks**
- Seed mean score **>= 0.75**
- mean Seed-minus-Raw gain **>= 0.15**
- strict paired Seed win rate **>= 60%**
- paired-bootstrap 95% CI lower bound **> 0**
- Seed dual-verifier acceptance **>= 75%**
- no identity, integrity, resource-envelope, checkpoint, or protocol mismatch

The paired bootstrap is frozen at **4,000 samples, seed 0**.
## Frozen execution discipline

1. Push this preregistration as a separate commit and require clean GitHub CI before private inference begins.
2. Re-hash candidate implementation, model artifact, task file, answer key, and audit report immediately before the first private model call.
3. Run one paired Raw-vs-Seed campaign using the frozen task file and exact model. Resume is allowed only from an exact-identity checkpoint validated by the runner.
4. Do not inspect the answer key during candidate execution and do not alter tasks, observations, scorer, thresholds, prompts, protocol, or resource limits after inference begins.
5. Seal all task pairs before scoring. The scorer receives the private key only after campaign evidence is complete.
6. Publish only hashes, aggregate/per-task numeric scores, protocol metadata, and non-secret audit results. Keep private task/key contents outside Git.
7. If any frozen criterion fails, Gate 2 remains not empirically certified. The holdout becomes retired evidence and cannot be reused as fresh certification data after candidate changes.

## Interpretation boundary

A pass would certify this bounded Gate-2 scientific-method scaffold on one preregistered private/OOD campaign for the frozen Qwen3-8B substrate. It would **not** establish AGI, ASI, or recursive amplification by itself.

A fail does not erase the public development gains. It means the current Gate-2 candidate did not meet the full frozen transfer criterion and must not be promoted.

## Pre-inference checklist

- [x] candidate source committed and pushed
- [x] candidate CI green
- [x] private tasks and key created outside Git
- [x] structural task/key validation passed
- [x] independent identifiability audit passed
- [x] candidate/model/task/key/audit hashes recorded above
- [ ] preregistration commit pushed and CI green
- [ ] private inference started
