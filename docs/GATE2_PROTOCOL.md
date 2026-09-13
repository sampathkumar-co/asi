# Gate 2 Scientific-Method Protocol

Updated: 2026-09-13

## Purpose

Gate 2 tests whether the same underlying model becomes a better scientific investigator when wrapped in Project Seed's bounded scientific-method scaffold. The target capability is not trivia accuracy; it is disciplined hypothesis testing under hidden evidence.

Gate 2 remains separate from Gate 1. Gate 1 established a strong bounded baseline agent. Gate 2 asks whether a structured research protocol improves falsification, prediction, evidence-driven revision, control handling, confound detection, and independent verification.

## Paired comparison

Each task is run twice with the exact same local model artifact and the same resource envelope:

- **Raw** — direct interactive investigation without the Seed scientific-method scaffold.
- **Seed** — falsifiable action, blind forecasts, reveal, mechanical comparison, revision, and verification.

The candidate never receives the private answer key. Hidden observations are withheld until the selected experiment is committed.

## Seed research loop

Before any experiment result is revealed:

1. make one blind model call that sees only the public question, declared hypotheses, experiment descriptions, and declared possible outcomes;
2. for every possible outcome, attribute the declared hypothesis or hypotheses whose truth would make that outcome a natural/direct result;
3. fail closed unless every experiment and every declared outcome is covered exactly once, each support set is non-empty, contains only declared hypothesis IDs, and contains no duplicates;
4. convert the support relation mechanically into canonical likelihoods: support-consistent outcomes receive weight **3**, unsupported outcomes weight **1**, then each hypothesis/experiment row is normalized; if a hypothesis supports all or none of an experiment's outcomes, that row remains uniform;
5. compute expected information gain from those runner-generated likelihoods and mechanically select the unused experiment with maximum information gain;
6. ask the model only for declared controls and risks for the already selected experiment; this call cannot choose a different experiment and receives no unrevealed result;
7. reveal that experiment's hidden outcome, update the Bayesian posterior mechanically, and derive rejected alternatives using the fixed Bayes-factor rule;
8. repeat selection/reveal/update up to the task's experiment limit;
9. mechanically fix the final posterior winner and rejection set; the final model call may explain the conclusion but cannot override them;
10. run distinct independent and adversarial verifier calls.

The model never supplies cross-hypothesis probability magnitudes. This prevents arbitrary confidence calibration (for example 100% versus 85% for the same qualitative prediction) from determining the trusted posterior. The raw attribution relation and runner-generated canonical likelihood matrix are both retained in evidence.

## Verification contract

Each verifier returns the declared hypothesis IDs it judges tied for strongest support, a `has_direct_evidence_defect` boolean, confidence, declared risks, and rationale. Generic residual uncertainty belongs in risks and does not by itself become a hard defect.

The trusted runner independently computes cumulative support from the frozen canonical likelihood assigned to each observed outcome. A verifier verdict passes only when the final hypothesis is the **unique** mechanical best, the model verifier supports only that same hypothesis, and no direct evidence/protocol defect is present. Verifier confidence means confidence in the support-set audit, not posterior mass. Seed acceptance requires both independent and adversarial verdicts to pass with confidence >= 0.8.

## Fail-closed behavior

Invalid IDs, repeated experiments, malformed JSON, schema violations, budget exhaustion, checkpoint hash mismatch, model/resource mismatch, and implementation mismatch fail closed.

A bounded repair call may correct malformed JSON or schema representation. Repairs are explicit `gate2_repair` calls, receive no hidden answer key or unrevealed outcome, are recorded in evidence, and consume the same common resource envelope.

Responses rejected after token accounting remain hashed into the transcript with `budget_accepted=false`; they do not silently disappear.

## Frozen development envelope

For both Raw and Seed:

- max steps: **16**;
- max model calls: **16**;
- max tool calls: **0**;
- max tokens: **15,000**;
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