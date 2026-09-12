# Gate 2 Scientific-Method Protocol

Updated: 2026-09-12

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
2. before reveal, forecast that experiment independently once for **each hypothesis** as an integer probability distribution over every declared outcome;
3. validate that supplied probabilities use only declared outcome IDs, are integers in 0..100, and sum to exactly 100; an omitted declared outcome is normalized to zero only when the supplied declared probabilities already sum to 100;
4. derive each hypothesis's categorical prediction mechanically from the probability argmax for rubric compatibility;
5. reveal only that experiment's observed outcome and observation;
6. mechanically accumulate hypothesis support by multiplying the frozen pre-reveal probability assigned to each observed outcome across experiments;
7. revise the best-supported hypothesis, explicitly reject contradicted alternatives, and update risks;
8. repeat until the task's experiment limit is reached, then produce a final report;
9. run distinct independent and adversarial verifier calls.

Probability distributions preserve graded pre-evidence commitments without forcing arbitrary categorical distinctions. Exact cumulative-likelihood ties remain ambiguity and block trusted acceptance.

## Verification contract

Each verifier returns the declared hypothesis IDs it judges tied for strongest support, a `has_direct_evidence_defect` boolean, confidence, declared risks, and rationale. Generic residual uncertainty belongs in risks and does not by itself become a hard defect.

The trusted runner independently computes the cumulative frozen-likelihood support set. A verifier verdict passes only when the final hypothesis is the **unique** mechanical best, the model verifier supports only that same hypothesis, and no direct evidence/protocol defect is present. Seed acceptance requires both independent and adversarial verdicts to pass with confidence >= 0.8.

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