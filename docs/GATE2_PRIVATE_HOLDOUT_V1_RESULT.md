# Gate 2 Private Holdout v1 — Result

Date: 2026-09-12

## Verdict

Gate 2 remains **NOT EMPIRICALLY CERTIFIED** on private holdout v1.

The frozen Seed candidate transferred strongly on task score, but the preregistered verifier-acceptance criterion failed. No threshold or verifier rule was changed after inference.

## Frozen identities

- candidate source commit: `ec1e98315a0baa2fe47d344702790b86bbc6132f`
- preregistration commit: `2126f64b7d37964edf019794507cd19d021f2fd8`
- implementation digest: `49c9db731136a98c0bef78627fd3952d5e2b9b1b1030eb8e6dbc7c5d4647ea7a`
- model: `qwen3:8b`
- model digest: `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`
- task SHA-256: `783007f2eb64df009d359f1ee853e084d244a9a6d34adfbe963c6bdee2c1c146`
- answer-key SHA-256: `43b38aa2728649e17fe9fc5fdfeb4d1695b34bd29972f4506d146ae3092b24a8`
- pre-inference audit SHA-256: `72500f029a9a456cdfad4d81b0cc55d65d13b434e7077fe8ff7f401713e13a20`
- sealed evidence file SHA-256: `13d630283730384686150ac17e7da9697657cd9749bdde32b973a4dfdd48915e`
- evidence content hash: `aaae0ebbe14836b47a545da77d7702e417a616b0321625c0174b107834a96b36`
- score content hash: `a6c7b330d3048d1237f21e3fcafd01a9a31ae34317325c3751b29a0f5986dcb6`
- score-file SHA-256: `ed7e9c3ae654f62762baa5bde1a3c86b457e3a8e47dad454ef8790f3f5900168`
- published sanitized score-artifact SHA-256: `c0959565d3df3266d09603e561fac9332900c930fc469f5ca3b75395b31dca2e`

## Preregistered metrics

| Metric | Frozen criterion | Observed | Pass |
|---|---:|---:|---|
| Valid paired tasks | >= 16 | **18** | yes |
| Seed mean score | >= 0.75 | **0.94167** | yes |
| Mean Seed-minus-Raw gain | >= 0.15 | **+0.23611** | yes |
| Strict Seed win rate | >= 60% | **66.67%** | yes |
| Paired-bootstrap 95% CI lower bound | > 0 | **+0.11944** | yes |
| Seed dual-verifier acceptance | >= 75% | **50.00% (9/18)** | **no** |

The bootstrap interval was **[+0.11944, +0.37222]**, using the frozen 4,000 paired samples with seed 0.

Raw mean was **0.70556**. Seed mean was **0.94167**. One Raw arm (`PRV07_DIAGNOSTIC`) failed closed after an audited repair attempt; all 18 Seed arms completed.

## Per-task numeric result

| Task | Raw | Seed | Seed verifier accepted |
|---|---:|---:|---|
| PRV01_FERTILIZER | 0.925 | 1.000 | yes |
| PRV02_ASSAY_BATCH | 0.425 | 1.000 | no |
| PRV03_SATELLITE | 0.425 | 1.000 | yes |
| PRV04_PLACEBO | 0.800 | 0.925 | yes |
| PRV05_RECOMMENDER | 0.425 | 0.900 | no |
| PRV06_BATTERY | 0.525 | 1.000 | no |
| PRV07_DIAGNOSTIC | 0.000 | 1.000 | yes |
| PRV08_NOVELTY | 0.925 | 0.925 | yes |
| PRV09_FRAUD_POLICY | 1.000 | 1.000 | no |
| PRV10_ROBOTICS | 1.000 | 1.000 | yes |
| PRV11_ECON_SEASON | 0.800 | 0.925 | yes |
| PRV12_LLM_FORMAT | 0.425 | 0.425 | no |
| PRV13_REGRESSION | 0.825 | 1.000 | no |
| PRV14_NETWORK | 0.525 | 0.925 | no |
| PRV15_COMPILER | 0.850 | 1.000 | no |
| PRV16_EDUCATION | 1.000 | 1.000 | yes |
| PRV17_SENSOR_LAG | 0.825 | 0.925 | yes |
| PRV18_SURVIVORSHIP | 1.000 | 1.000 | no |

## Interpretation

The private/OOD run provides strong evidence that the scientific-method scaffold improves this fixed Qwen3-8B substrate on the weighted research rubric under the frozen resource envelope. The gain is statistically positive under the preregistered paired bootstrap and the strict-win criterion also passes.

Certification nevertheless fails because the dual-verifier acceptance rate is materially below the frozen threshold. The verifier criterion was part of the scientific contract before private inference, so it cannot be discarded merely because the task scores are strong.

This failure is therefore narrower than a failure of task-level transfer: it identifies verifier reliability/calibration as the dominant unresolved Gate-2 bottleneck for this candidate.
## Holdout retirement and next-step rule

Private holdout v1 is now **retired evidence**. It must never again be treated as fresh certification data after any candidate, prompt, verifier, scorer, or protocol change.

Future Gate-2 development may analyze this retired evidence, but any improved candidate requires a newly created and independently audited private/OOD holdout with a new preregistration before another certification attempt.

No private task text, private answer text, or full private campaign evidence is committed. The public repository contains only hashes, this numeric result record, and the sanitized score artifact.

Sanitized machine-readable score: [`../artifacts/gate2-private-holdout-v1-score.json`](../artifacts/gate2-private-holdout-v1-score.json).

Preregistration: [`GATE2_PRIVATE_HOLDOUT_V1_PREREGISTRATION.md`](GATE2_PRIVATE_HOLDOUT_V1_PREREGISTRATION.md).
