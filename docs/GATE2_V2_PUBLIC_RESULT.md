# Gate 2 v2 Public Development Result

Updated: 2026-09-12

This is **development evidence, not certification**. The eight public tasks were observed repeatedly during protocol development and cannot serve as a private/OOD promotion benchmark.

## Candidate identity

- pre-commit implementation digest: `d8a028f394121ca3dc6e5c890304bd3d13cd03e5566467befecb31190540b340`
- model: `qwen3:8b`
- model digest: `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`
- envelope: 16 steps, 16 model calls, 0 tools, 15,000 tokens, $0
- deterministic qualification: **36/36 PASS**
- repository regression: **157/157 PASS** with `ResourceWarning` as error

## Public identities

- task SHA-256: `82099cbd17c63c53d8b08af4f2b1ee561b4f22448af373abffdc68e100939b51`
- answer-key SHA-256: `ea2affbda2d53e478414efab3041290fecc0be403779ceee38541a382e9266a4`
- evidence content hash: `5db6f27ff34fe0138a2f499361960ac63b32faa4b9d56fa1a2bd355a97a5197a`
- evidence-file SHA-256: `13258ebf0a6bc405a2683cf98f4531fdb8e929f026b2319efab54562e448782f`
- score content hash: `15cc46330eb28a212ca91a045ba12ba86c066c80a3217ac620e567b0f742629f`

## Result

- valid pairs: **8**
- Raw mean: **0.75625**
- Seed mean: **0.94375**
- mean gain: **+0.18750**
- strict Seed wins: **6/8 = 75%**
- paired-bootstrap 95% CI: **[+0.025, +0.35]**
- Seed independent+adversarial acceptance: **8/8 = 100%**
- Seed final hypothesis: **H2 on all 8 tasks**
- Seed repairs: **0**
- Seed budget failures: **0**

All eight Seed arms had H2 as the unique trusted cumulative-likelihood winner. Every frozen numerical promotion check passes except `valid_pairs >= 16`. Therefore `promotion_pass=false` by construction on this public suite.

## Interpretation

V2 resolves the verifier false-negative problem observed on private v1 without weakening the verifier-acceptance threshold. It also replaces brittle categorical collision rescue with graded blind forecasts and trusted mechanical likelihood support. The next certification attempt must use a brand-new external, independently audited, preregistered private/OOD holdout.
