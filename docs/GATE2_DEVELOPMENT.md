# Gate 2 Development Record

Updated: 2026-09-12

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
## Post-freeze private holdout v1 result

The frozen source commit `ec1e98315a0baa2fe47d344702790b86bbc6132f` and preregistration commit `2126f64b7d37964edf019794507cd19d021f2fd8` both passed CI before private inference.

On 18 balanced private/OOD tasks, Raw mean was **0.70556** and Seed mean **0.94167**, producing **+0.23611** mean gain. Strict Seed wins were **66.67%** and the 4,000-sample paired-bootstrap interval was **[+0.11944, +0.37222]**.

Seed verifier acceptance was **9/18 = 50%**, below the preregistered **75%** threshold. Therefore the private run does not promote Gate 2 even though all score-based transfer checks pass.

This holdout is now retired. The next development cycle may study its verifier failures, but no changed candidate may claim certification on these same 18 tasks. A later certification attempt requires a completely new independently audited and preregistered private/OOD holdout.

See [`GATE2_PRIVATE_HOLDOUT_V1_RESULT.md`](GATE2_PRIVATE_HOLDOUT_V1_RESULT.md).

## Gate-2 v2 verifier/research development

Private v1 failed only the verifier-acceptance criterion. Diagnostic review showed that eight correct Seed conclusions were rejected largely because model verifiers converted generic residual uncertainty into hard defects. The v2 cycle therefore changed verifier semantics without weakening any promotion threshold.

Several categorical forecast-rescue designs were tested and rejected during development: global planning, collision audits, anchored collision refinement, and all-tie experiment fallback. Stress tests showed that categorical collision prompts could hallucinate distinctions or mutate otherwise-correct forecasts. Those rescue paths are **not** part of v2.

The v2 candidate instead records one blind **probability distribution over declared outcomes per hypothesis per experiment before reveal**. The runner derives categorical argmax predictions for the unchanged scoring rubric, while trusted verifier support is the cumulative product of the frozen probability assigned to each observed outcome. Exact ties remain failures rather than being forced apart.

Verifier model outputs are also structured: they name every declared hypothesis tied for strongest support and flag only concrete direct evidence/protocol defects. The runner accepts a verifier only when the final hypothesis is the unique mechanical likelihood winner, the verifier supports only that hypothesis, and no direct defect exists.

Current pre-commit v2 implementation digest:
`d8a028f394121ca3dc6e5c890304bd3d13cd03e5566467befecb31190540b340`.

Deterministic qualification: **36/36** canaries. Repository regression: **157/157** tests with `ResourceWarning` promoted to an error, plus clean `compileall` and `git diff --check`.

Common Raw/Seed envelope: **16 steps / 16 model calls / 0 tools / 15,000 tokens / $0**. Model remains local `qwen3:8b` digest `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`.

### v2 public development result

Fresh eight-pair evidence content hash: `5db6f27ff34fe0138a2f499361960ac63b32faa4b9d56fa1a2bd355a97a5197a`.
Evidence-file SHA-256: `13258ebf0a6bc405a2683cf98f4531fdb8e929f026b2319efab54562e448782f`.
Score content hash: `15cc46330eb28a212ca91a045ba12ba86c066c80a3217ac620e567b0f742629f`.

Raw mean **0.75625**; Seed mean **0.94375**; mean gain **+0.18750**; strict Seed wins **6/8 = 75%**; paired-bootstrap CI **[+0.025, +0.35]**; Seed verifier acceptance **8/8 = 100%**. Every Seed arm succeeded with final H2, unique mechanical likelihood support for H2, zero repairs, and no budget failure.

This development run passes every frozen numerical criterion except `valid_pairs >= 16`, which cannot be satisfied by the eight-task public suite by construction. It is **not** certification evidence. The public suite has been repeatedly observed and remains retired for certification.

### v2 private certification result

Frozen candidate `261cc0d486830b3219a58d499661ccf1c7f1327b` and preregistration `f7a461881e691640f0a822548bd39de473ef2536` both passed CI before inference. On 18 balanced private/OOD pairs, Raw mean was **0.81250** and Seed mean **0.82083**, for only **+0.00833** mean gain. Strict Seed wins were **33.33%**, bootstrap CI **[-0.07361, +0.09583]**, and verifier acceptance **88.89%**.

Thus v2 fixed the dominant v1 verifier false-negative failure but did not demonstrate the preregistered incremental capability gain. Mean gain, strict-win rate, and positive-CI checks failed; Gate 2 remains uncertified. Private v2 is permanently retired. See [`GATE2_PRIVATE_HOLDOUT_V2_RESULT.md`](GATE2_PRIVATE_HOLDOUT_V2_RESULT.md).

The next legitimate development cycle is **v3**, focused on actual Raw-to-Seed capability gain rather than further verifier-threshold tuning. Private v1/v2 may be used only diagnostically. Any new certification attempt requires a new frozen candidate and a completely new audited/preregistered private/OOD holdout.
