# Gate 2 Development Record

Updated: 2026-09-11

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