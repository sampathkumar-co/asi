# Gate 2 Certification Plan

Updated: 2026-09-11

## Status

Gate 2 is **not empirically certified**. The candidate is being frozen after public development calibration. Certification requires a new private/OOD campaign created and audited after candidate freeze and before model inference.

## Frozen promotion rule

A Gate-2 certification attempt passes only if all of the following are true:

- valid paired tasks >= **16**;
- Seed mean >= **0.75**;
- mean Seed-minus-Raw gain >= **0.15**;
- strict Seed win rate >= **60%**;
- deterministic paired-bootstrap lower confidence bound > **0**;
- Seed independent+adversarial acceptance >= **75%**;
- Raw and Seed use the same model artifact and resource envelope;
- all campaign, pair, checkpoint, implementation, model, and answer-key integrity checks pass;
- no candidate prompt contains the private answer key or unrevealed observation.

The paired bootstrap is fixed at 4,000 samples with random seed 0.

## Freeze-before-holdout sequence

1. commit the Gate-2 candidate, public calibration record, tests, and protocol documentation;
2. push the candidate commit and require clean GitHub Actions CI;
3. record the frozen candidate commit, implementation digest, model digest, resource envelope, scorer/rubric, and thresholds;
4. create the private/OOD task file and answer key **outside the repository**;
5. independently audit every private task/key pair before inference;
6. record only cryptographic hashes and non-secret metadata in the preregistration;
7. commit and push the preregistration and require clean CI;
8. only then run Raw and Seed inference on the private tasks.
## Holdout requirements

The private suite must contain at least 16 paired research tasks and must not reuse the eight public calibration tasks as certification data. It should cover multiple scientific failure modes rather than one template family.

The private answer key must remain external to GitHub and external to candidate prompts. Task and key files must have independent SHA-256 hashes recorded before inference.

The candidate implementation, model artifact, resource envelope, scoring weights, acceptance rule, bootstrap procedure, and promotion thresholds become immutable once private inference starts.

## Evidence handling

The campaign must checkpoint atomically after each sealed pair. Resume is allowed only when suite, model, model manifest, implementation manifest, settings, task-file hash, and previously sealed pair hashes match exactly.

Malformed output, invalid IDs, repeated experiments, verifier disagreement, resource overspend, or integrity mismatch fail closed according to the frozen protocol. Bounded repair remains permitted only because it is already part of the frozen candidate and consumes the shared envelope.

Raw evidence and private task/key contents remain external. GitHub may contain sanitized score artifacts, hashes, preregistration metadata, and the final audit report.

## No post-inference tuning

After the first private candidate call, do not change the candidate, scorer, thresholds, task file, answer key, or verifier policy based on holdout outcomes. A failed campaign remains failed evidence.

If an evaluator implementation bug is discovered after inference, stop the certification claim, preserve all sealed artifacts, document the incident, and resolve it transparently. Do not silently alter sealed research evidence.

## Interpretation

Passing Gate 2 would show that the frozen Seed scientific-method scaffold improves a fixed model on a preregistered hidden/OOD research benchmark under normalized resources. It would **not** by itself establish AGI, ASI, autonomous recursive self-improvement, or sustained recursive amplification.