# Gate 2 vNext Private Holdout - Preregistration

Date: 2026-09-14

## Purpose

This document preregisters the private/OOD certification attempt for the frozen post-v31 Gate-2 vNext candidate. It is written after candidate freeze, successful freeze CI, creation of a completely new external holdout, and independent structural/key/overlap audit, but **before any private-vNext model inference**.

The public calibration suite and private holdouts v1, v2, and v3.1 are retired or development-only evidence. None is reused as fresh certification data.

## Frozen candidate identity

- source commit: `ce67ac5517115af85b0ce5b424426d0c1a1d351f`
- commit message: `Freeze Gate 2 vNext candidate`
- public-result record commit immediately below freeze: `641ecf3e3cb3315a5a0f8839fca3ada78d2ec797`
- Gate-2 implementation digest: `56707e7012af796b21c0304d6f2b3f4a903b95655dee28abd4181cc9a308bdf3`
- deterministic Gate-2 qualification: **59/59 PASS**
- qualification content hash: `7df14fe831d3d1f5b5f247bb3e244080763e955b139c377ed06f4c833dc88fde`
- local repository regression: **181/181 PASS**
- compileall: **PASS**
- Git diff hygiene: **PASS**
- Markdown link audit at freeze preparation: **43 project files, 0 missing links**
- GitHub Actions freeze CI: run **#162**, run id `34805034240`, conclusion **success**

No candidate source, scorer, verifier policy, preflight policy, repair policy, protocol, resource limit, likelihood rule, scoring weight, or promotion threshold may change for this holdout attempt after preregistration.

## Frozen model identity

- provider: local Ollama
- model: `qwen3:8b`
- model manifest SHA-256: `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`
- model artifact size recorded for this digest: `5225388164` bytes
- temperature: `0.0`
- thinking mode: disabled
- context window: `4096`

## Frozen public-development identity

The public suite is **not** certification evidence. These hashes bind the development record used to freeze this candidate.

- public suite id: `gate2-public-calibration-v1`
- public task SHA-256: `82099cbd17c63c53d8b08af4f2b1ee561b4f22448af373abffdc68e100939b51`
- public answer-key SHA-256: `ea2affbda2d53e478414efab3041290fecc0be403779ceee38541a382e9266a4`
- exact-candidate public evidence content hash: `d6ae21e88c39d71bf46d42cb419c889d005b886283047ee51f0fbb3cc95aa0ce`
- exact-candidate public evidence file SHA-256: `574a25101c08e0fba0b13c0913c22feb18e53796e86ece25df2319098a896705`
- exact-candidate public score content hash: `7e89670867663b4fd770963f24c48baa5a9efea130024727cca9a5a2a4f61c55`
- normalized Git public score SHA-256: `f5c0a3be8cf1798a056c42f0985802bc79e986b0d96608dbb22e63b5929baf4e`
- public result: Raw **0.80000**, Seed **0.98750**, gain **+0.18750**, strict wins **87.5%**, CI **[+0.090625,+0.31875]**, verifier acceptance **100%**, zero repairs, zero execution incidents

## Frozen private holdout identity

The private files remain outside Git under `AppData/Local/ProjectSeed/gate2-private-holdout-vnext`. Only hashes and non-secret audit metadata are committed.

- suite id: `gate2-private-holdout-vnext`
- paired task count: **18**
- task-file SHA-256: `d58f17865603038c89e8230b86f1875290103f837e327ee2261b9992bc4743e1`
- answer-key SHA-256: `26ada4b16344793a82900134703c5270f104852863bcaabe120b85f8e1cb976c`
- audit-file SHA-256: `71bb763df62b6fb635575cde7c0d929c4ccf850a01ed9a037ab8465953e228c2`
- creation-metadata SHA-256: `c1a070ef0abeae6a31aad6ce15482d5f14c5b9be36d6fefc0ac90d5b2fab64a1`
- correct-label balance: **H1=6, H2=6, H3=6**
- E1/E2 outcome-label surface balance for each hypothesis: **A=12, B=12, C=12**
- exact task-id overlap with public/private-v1/private-v2/private-v31: **0**
- exact question overlap with public/private-v1/private-v2/private-v31: **0**
- maximum fuzzy question similarity to public/retired private suites: **0.583629893238**
- maximum internal question similarity: **0.591044776119**
- pre-inference fuzzy rejection guard: **0.72**; both external and internal audits **PASS**
- structural task/key validation: **PASS (18/18)**
- E1/E2 keyed outcomes uniquely identify the declared hypotheses on **18/18** tasks
- observed outcomes match the keyed final hypothesis on **18/18** tasks
- all tasks declare `max_experiments=2`
- no evidence file existed when this preregistration was prepared
- holdout creation and audit used **no model inference**

The answer key is never supplied to Raw or Seed prompts. Hidden observations remain inaccessible until the trusted runner reveals a selected experiment.

## Frozen execution-integrity policy

A fixed task-independent provider preflight runs before the first unfinished pair, outside the scored Raw/Seed envelope, with purpose `gate2_preflight`, an 8-token cap, and no automatic retry. Provider failure at preflight aborts before scored evidence.

During scored execution, provider/transport failures and trusted-runner failures are execution incidents. Any such incident makes `clean_execution=false`, so the campaign cannot promote. Model/protocol failures and budget exhaustion fail closed at arm level.

Schema recovery is capped at **two schema-repair calls total per arm**, shared across attribution/action/design/final/verifier stages. A second repair may recover a still-invalid first repair; a third schema repair is never attempted. Verifier repairs consume the same shared counter and are recorded in evidence.

## Common resource envelope

Both Raw and Seed use the same hard per-task envelope:

- maximum steps: **16**
- maximum model calls: **16**
- maximum tool calls: **0**
- maximum accepted tokens: **15,000**
- maximum API cost: **$0**

Normal Seed execution is six model calls: one pre-reveal outcome-attribution call, two runner-selected experiment design/control calls, final explanation, independent verifier, and adversarial verifier. Qualification proves the maximum three-experiment worst case including syntax repair and both schema-repair slots remains inside the unchanged model-call envelope: Raw **10**, Seed **16**.

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
- `clean_execution=true`
- no identity, integrity, resource-envelope, answer-key, or protocol mismatch

The paired bootstrap is fixed at **4,000 samples** with random seed **0**.

## Execution rule

Private inference may begin only after this preregistration commit is pushed and GitHub Actions is green on the exact preregistration SHA. After the first private model call, the candidate, scorer, thresholds, task file, answer key, verifier policy, preflight policy, repair policy, canonical 3:1 likelihood rule, and resource envelope are immutable for this attempt.

The campaign must run exactly once on this holdout. Resume is permitted only through the frozen checkpoint-identity rules. The frozen scorer may run only after all intended pairs have sealed or the campaign has terminated according to the frozen failure policy.

If the campaign fails, preserve it as failed evidence and do not tune or rerun on this holdout. If an evaluator implementation defect is discovered after inference, stop the certification claim, preserve all sealed artifacts, document the incident, and resolve it transparently rather than altering the sealed campaign.

A pass would certify this bounded Gate-2 scientific-method scaffold on one preregistered private/OOD campaign for the frozen Qwen3-8B substrate. It would **not** by itself establish AGI, ASI, autonomous recursive self-improvement, or sustained recursive amplification.
