# Gate 1 v4 Candidate Development

Updated: 2026-09-10

Status: **FROZEN FOR A NEW UNSEEN HOLDOUT; NOT PROMOTION EVIDENCE**

## Why v4 exists

Holdout v3 produced a large positive aggregate effect — Raw 3/16 (18.75%) versus Seed 11/16 (68.75%), +50 percentage points, with a 95% paired-bootstrap CI of [+18.75 pp, +81.25 pp]. Gate 1 still failed because strict Seed wins were 9/16 (56.25%), below the frozen >=60% requirement.

V301-V316 are therefore retired development evidence. They cannot be reused as fresh certification data after architecture changes.

## Frozen v4 candidate

- Source commit: `b4242af758b1222f8ecea0bf7306e917a36ed9d8`
- Seed implementation digest: `f9d882e185b235d0a8345640ee1577edb518be96dbf8af0f6b50ec204f5a1358`
- Attested implementation files: 27
- Local regression: **134/134 PASS** with `ResourceWarning` promoted to error
- Deterministic Gate-1 qualification: **10/10 PASS**
- Qualification content hash: `357b3beac3bbcfb04ccf09b6e00a74dd7fdd95b2ef9ae72f7dd15fc9cff16799`

## Generic reliability changes

The v4 candidate broadens deterministic shortest-path routing beyond literal `shortest path` wording. Minimum-cost directed routes, one-way networks, weighted arcs and shortest source-to-target paraphrases can now expose the exact `shortest_path` tool.

Assignment/CSP translation now supports explicit `positions_between`, position-not-equal normalization and stricter subject-first relation semantics. The planner is told not to inject unstated derived constraints.
The higher-level assignment tool also accepts a one-to-one `source_clues` provenance array. Each source clue is copied verbatim and used to bind entity identities before solving, so a model-side entity-pair substitution can be corrected or rejected instead of silently proving the wrong puzzle.

## Retired-v3 development probes

After v3 was sealed and scored, the five targeted failure cases were rerun only as development diagnostics:

- V301: graph router miss -> one-step verified shortest-path solution after semantic routing fix.
- V302: one-way-network router miss -> one-step verified shortest-path solution.
- V309: reversed `immediately after` relation -> one-step unique assignment after subject-first relation contract.
- V310: invented constraint / wrong positions-between / numeric-position mismatch -> one-step unique assignment with the declarative CSP extensions.
- V315: entity substitution across logic-grid clues -> one-step unique assignment using clue provenance.

These results demonstrate that the intended failure classes are closed on retired data. They do **not** change the official v3 score and do **not** certify Gate 1.

## Next promotion attempt

The next valid evidence must come from a new private holdout v4 created only after this candidate was frozen. Before inference:

1. generate materially new task instances;
2. independently audit correctness, uniqueness and optimality;
3. standardize the answer-key container to the repository scorer schema;
4. preregister task/key hashes, candidate/model identities, resource envelope and unchanged promotion thresholds;
5. run Raw and Seed without architecture changes;
6. score once and publish the result whether it passes or fails.

Gate 1 remains active until every preregistered promotion criterion is satisfied.