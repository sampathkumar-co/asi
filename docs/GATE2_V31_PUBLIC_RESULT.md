# Gate 2 v3.1 Public Development Result

Updated: 2026-09-13

## Status

**Development-qualified candidate; not Gate-2 certification.**

This run uses the repeatedly observed eight-task public development suite `gate2-public-calibration-v1`. It is useful for protocol development only and is permanently ineligible as private certification evidence.

Candidate implementation digest: `c0abee591ed723a46ba57b527c2189efc0d711f3d3a423866a611503e8f16ce8`.

Deterministic qualification: **46/46 PASS**; qualification content hash `50a481bfb667505ad95a0050a3fc82218b51a9a6fbadda7d405adc76f4f69799`.

Repository regression before and after the campaign: **157/157 PASS**, compileall PASS, `git diff --check` clean.

## Protocol

Seed uses one hidden-safe pre-reveal outcome-to-hypothesis causal-attribution call. The trusted runner validates complete experiment/outcome coverage, converts support relations into fixed **3:1** canonical likelihood weights, computes information gain, selects experiments, updates Bayesian posteriors, derives Bayes-factor rejections, and fixes the final hypothesis mechanically.

Normal Seed usage is six model calls: attribution, two design/control calls, final explanation, independent verifier, adversarial verifier. The model does not provide probability magnitudes or choose the final posterior winner.
## Frozen identities

- model: `qwen3:8b`;
- model digest: `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`;
- task SHA-256: `82099cbd17c63c53d8b08af4f2b1ee561b4f22448af373abffdc68e100939b51`;
- answer-key SHA-256: `ea2affbda2d53e478414efab3041290fecc0be403779ceee38541a382e9266a4`;
- evidence content hash: `b760625388757dd810785d474e5777cd1fed8d0c89d83790f04df3de4f8273ce`;
- evidence file SHA-256: `81e89e8665d382bb73b4d1dc706d6d7626e0cb7ae21b69861cbe3d7f1c70556d`;
- score content hash: `b7ab06da04797bbeebe189d9e9dbb19b9e48ac1da1c305c2d37b9df7f4269be6`;
- external score-file SHA-256: `adab1524e2a407496098f242c089767fd2333ce917873220758682471c6e9500`;
- normalized Git score artifact SHA-256: `92f48ef5ce8fdf80c915a3f136a33ee84456ca2a7a4b49a85768e76c9016b43c`;
- resource envelope: 16 steps / 16 model calls / 0 tools / 15,000 tokens / $0.

## Result

- valid pairs: **8**;
- Raw mean: **0.76875**;
- Seed mean: **0.98750**;
- mean Seed-minus-Raw gain: **+0.21875**;
- strict Seed wins: **6/8 = 75%**;
- 4,000-sample paired-bootstrap CI: **[+0.06250, +0.46875]**;
- Seed verifier acceptance: **8/8 = 100%**.
All eight Seed arms succeeded, selected **E1 then E2**, finished with mechanical posterior `H2=0.81818`, used **6 model calls**, remained below 8,400 tokens, required **zero repairs**, and were accepted by both verifiers.

All frozen numerical promotion criteria except `valid_pairs >= 16` pass on this public run. `promotion_pass=false` is therefore expected because this development suite contains only eight pairs.

## Interpretation

Compared with v2 public calibration, v3.1 raises Seed from **0.94375 to 0.98750** and gain from **+0.18750 to +0.21875**, while retaining 75% strict wins and 100% verifier acceptance. Compared with failed v3, it reverses the gain from **-0.22813 to +0.21875** and repairs the forecast-collision failures on CAL02, CAL03, CAL05, CAL06, and CAL08.

Because the public suite and answer key were repeatedly inspected during development, this result is **not independent evidence of transfer**. The candidate must be frozen before a newly generated, externally stored, audited, preregistered private/OOD holdout is used.

Sanitized score artifact: [`../artifacts/gate2-v31-public-calibration-score.json`](../artifacts/gate2-v31-public-calibration-score.json).