# Gate 2 Scientific-Method Protocol

Updated: 2026-09-11

## Purpose

Gate 2 tests whether the same underlying model becomes a better scientific investigator when wrapped in Project Seed's bounded scientific-method scaffold. The target capability is not trivia accuracy; it is disciplined hypothesis testing under hidden evidence.

Gate 2 remains separate from Gate 1. Gate 1 established a strong bounded baseline agent. Gate 2 asks whether a structured research protocol improves falsification, prediction, evidence-driven revision, control handling, confound detection, and independent verification.

## Paired comparison

Each task is run twice with the exact same local model artifact and the same resource envelope:

- **Raw** — direct interactive investigation without the Seed scientific-method scaffold.
- **Seed** — falsifiable action, blind forecasts, reveal, mechanical comparison, revision, and verification.

The candidate never receives the private answer key. Hidden observations are withheld until the selected experiment is committed.

## Seed research loop

For each permitted experiment:

1. choose the currently best-supported hypothesis, an unused experiment, controls, rejected hypotheses, and material risks;
2. before reveal, forecast the selected experiment independently once for **each hypothesis**;
3. on the first experiment only, if the selected hypothesis has the same forecast as exactly one competing hypothesis, optionally run one blind two-way collision audit;4. reveal only that experiment's observed outcome and observation;
5. mechanically compare every frozen forecast with the revealed outcome;
6. revise the best-supported hypothesis, explicitly reject contradicted alternatives, and update risks;
7. repeat until the task's experiment limit is reached, then produce a final report;
8. run distinct independent and adversarial verifier calls.

Three-way forecast collisions are deliberately **not** forced apart. Ambiguity is preserved rather than converted into fabricated discrimination.

## Verification contract

Verifiers do not emit a trusted `pass`/`fail` label. They return a structured `has_material_defect` boolean, confidence, declared risks, and rationale. The trusted runner derives the verdict from that boolean.

Seed acceptance requires both independent and adversarial verdicts to pass with confidence >= 0.8. Verifier disagreement blocks acceptance.

## Fail-closed behavior

Invalid IDs, repeated experiments, malformed JSON, schema violations, budget exhaustion, checkpoint hash mismatch, model/resource mismatch, and implementation mismatch fail closed.

A bounded repair call may correct malformed JSON or schema representation. Repairs are explicit `gate2_repair` calls, receive no hidden answer key or unrevealed outcome, are recorded in evidence, and consume the same common resource envelope.

Responses rejected after token accounting remain hashed into the transcript with `budget_accepted=false`; they do not silently disappear.

## Frozen development envelope

For both Raw and Seed:

- max steps: **16**;
- max model calls: **16**;
- max tool calls: **0**;
- max tokens: **12,000**;
- max cost: **$0**.
The evaluated local model is `qwen3:8b`, model digest `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`, temperature 0, thinking disabled, context 4096.

## Scoring rubric

Each arm is scored from 0 to 1:

- correct final hypothesis: **0.40**;
- first experiment is discriminating: **0.15**;
- at least one informative experiment: **0.05**;
- pre-evidence predictions consistent with the key: **0.15**;
- required controls: **0.10**;
- evidence-driven rejection/revision: **0.10**;
- critical risk/confound detection: **0.05**.

Failed arms score zero. The paired bootstrap uses 4,000 samples with deterministic seed 0.

## Promotion criteria

A certification campaign must satisfy all of the following without post-run threshold changes:

- at least **16 valid paired tasks**;
- Seed mean score >= **0.75**;
- mean Seed-minus-Raw gain >= **0.15**;
- strict Seed win rate >= **60%**;
- paired-bootstrap lower confidence bound > **0**;
- independent + adversarial Seed acceptance >= **75%**;
- no identity, integrity, resource-envelope, protocol, or private-key separation failure.

These are certification criteria, not a promise that the eight-task public development suite will pass them.