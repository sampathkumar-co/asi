# Gate-2 vNext Structured-Output Public Development Result

Status: **development evidence only; Gate 2 remains NOT certified.**

This result evaluates the post-v31 development tree after two generic integrity changes: explicit execution-failure classification and purpose-specific Ollama JSON Schemas for Gate-2 model calls. It does not use a new private holdout and does not authorize reuse of any retired private evidence.

## Candidate identity

- model: `qwen3:8b`
- model digest: `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`
- development implementation digest: `56d144466987e62295830dc3335fda4dde1ebafb4dfb4a6d65563cc92f25bb82`
- qualification: **54/54 PASS**
- qualification hash: `71401491db4d22ec3111c5e109319cb623ad4ed8f9f51c5942675842dfee18d2`
- repository regression: **168/168 PASS** plus compileall and diff hygiene

## Structured-output change

Ollama now receives bounded static JSON Schemas for Raw actions, Seed outcome attribution, Seed design, Raw/Seed final reports, and independent/adversarial verifier responses. These schemas constrain only field presence, primitive types, bounded strings, ranges, arrays, and uniqueness. They do not contain task-specific hypothesis, experiment, outcome, control, risk, answer-key, or private-holdout identities.

`gate2_repair` intentionally remains generic JSON because its target object depends on the failed stage; dynamic scientific IDs continue to be checked by the trusted runner.

## Live backend qualification

Before the full public suite, a two-task public smoke completed with the expected **18 model calls**, **zero repairs**, no execution incidents, Seed **1.000**, Raw **0.7125**, and gain **+0.2875**. This was only a compatibility/reliability smoke and is not promotion evidence.

The full eight-task public-development suite then completed **8/8 pairs** with **88 journal events**, **zero repair calls**, and **zero execution incidents**.

## Public-development score

- Raw mean: **0.821875**
- Seed mean: **0.98750**
- mean gain: **+0.165625**
- strict Seed wins: **6/8 = 75%**
- paired-bootstrap CI: **[+0.06250, +0.303125]**
- Seed verifier acceptance: **8/8 = 100%**
- campaign valid: **true**
- promotion pass: **false**, because the repeatedly observed public suite contains only 8 pairs versus the frozen minimum of 16

## Comparison with frozen v3.1 public development

The previous public v3.1 run scored Raw **0.76875**, Seed **0.98750**, gain **+0.21875**, strict wins **75%**, CI **[+0.06250, +0.46875]**, and verifier acceptance **100%**.

Seed is unchanged task-for-task in the structured-output run. The lower measured gain comes entirely from a healthier Raw baseline: `CAL01_SELECTION` improves from **0.000** to **0.425** instead of failing closed, while every other Raw task score and every Seed task score remain unchanged. This is desirable evaluator behavior because a shared reliability improvement helps both arms rather than creating an artificial Seed advantage.

## Evidence identity

- evidence content hash: `ef4ec68d123d43950be8c63ef1ca7ec5df831117f1d40526c0fd22c66ff305e7`
- evidence file SHA-256: `c4e2178f192c158d357d1e4707cc824773065878b4587615320cb273f6592afe`
- answer-key SHA-256: `ea2affbda2d53e478414efab3041290fecc0be403779ceee38541a382e9266a4`
- score content hash: `5316e7fd71653f77bfc7a709da83eaa8339f59bd74f6c7709ea4352f2d93944c`
- external score-file SHA-256: `606429cf3cfc0c4d81ac9bb3bd330864db12f62e6dc508b2a986e107d4ba18d2`
- LF-normalized repository score SHA-256: `22cad2cb1153c327603b5d75d3d414c3f74dc977c0e0b81b0ec349ee4123e4c1`

Sanitized score artifact: [`../artifacts/gate2-vnext-structured-public-score.json`](../artifacts/gate2-vnext-structured-public-score.json).

## Interpretation

This is a development milestone, not certification. The public suite has been repeatedly inspected and has only eight tasks. A future certification attempt still requires a newly frozen candidate, green CI, a completely fresh external private/OOD holdout created after the freeze, preregistration, preregistration CI, and only then inference under the unchanged promotion thresholds.
