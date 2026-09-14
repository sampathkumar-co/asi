# Gate-2 vNext Final Public Development Result

Status: **development evidence only; Gate 2 remains NOT certified.**

This run evaluates the exact post-v31 vNext tree after execution-integrity classification, task-independent structured-output schemas, provider-readiness preflight, and bounded schema repair. It uses only the repeatedly observed eight-task public suite and cannot certify Gate 2.

## Candidate identity

- source commit before result-record documentation: `62bf1db71f329abc095d8122214c551f3e1a9cd7`
- model: `qwen3:8b`
- model digest: `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`
- development implementation digest: `56707e7012af796b21c0304d6f2b3f4a903b95655dee28abd4181cc9a308bdf3`
- repository regression: **181/181 PASS** plus compileall and diff hygiene
- deterministic qualification: **59/59 PASS**
- qualification hash: `7df14fe831d3d1f5b5f247bb3e244080763e955b139c377ed06f4c833dc88fde`

## Reliability boundary

Provider/transport and trusted-runner failures invalidate a campaign. A fixed task-independent provider preflight runs before the first unfinished scored pair. Normal Gate-2 calls use purpose-specific JSON Schemas. Schema recovery is capped at **two repair calls total per arm**, shared across all stages and verifiers. Qualification proves worst-case three-experiment usage of Raw **10** and Seed **16** model calls inside the unchanged 16-call envelope.

## Exact-candidate public run

The full public-development campaign sealed **8/8 pairs**. The progress journal contains the provider-preflight event first, followed by normal pair execution. All Raw and Seed arms succeeded, Seed verifier acceptance was **8/8 = 100%**, and there were **zero schema-repair calls** and **zero execution incidents**.

## Public-development score

- Raw mean: **0.80000**
- Seed mean: **0.98750**
- mean gain: **+0.18750**
- strict Seed wins: **7/8 = 87.50%**
- paired-bootstrap CI: **[+0.090625, +0.31875]**
- Seed verifier acceptance: **100%**
- campaign valid: **true**
- promotion pass: **false only because valid pairs = 8 < frozen minimum 16**

Every other frozen promotion check passes on this public development run. These checks remain development diagnostics only because this suite and answer key have been repeatedly inspected.

## Evidence identity

- evidence content hash: `d6ae21e88c39d71bf46d42cb419c889d005b886283047ee51f0fbb3cc95aa0ce`
- evidence file SHA-256: `574a25101c08e0fba0b13c0913c22feb18e53796e86ece25df2319098a896705`
- answer-key SHA-256: `ea2affbda2d53e478414efab3041290fecc0be403779ceee38541a382e9266a4`
- score content hash: `7e89670867663b4fd770963f24c48baa5a9efea130024727cca9a5a2a4f61c55`
- external score-file SHA-256: `f69c77f6ec234e632bf060e86b273af7c0b4d012cecbabafa3360b99525f3e5a`
- LF-normalized repository score SHA-256: `f5c0a3be8cf1798a056c42f0985802bc79e986b0d96608dbb22e63b5929baf4e`

Sanitized score artifact: [`../artifacts/gate2-vnext-final-public-score.json`](../artifacts/gate2-vnext-final-public-score.json).

## Interpretation

Compared with the prior structured-output public run, Seed remains **0.98750** and verifier acceptance remains **100%**. Raw moves from **0.821875** to **0.80000**, so measured gain rises from **+0.165625** to **+0.18750** and strict wins from **75%** to **87.5%**. This is compatible with normal model-output variance on a repeatedly observed development set; it is not new transfer evidence.

The candidate is now suitable for a separate freeze boundary. After freeze CI is green, any certification attempt must create a completely fresh external private/OOD holdout after that freeze, audit it before inference, preregister it, require preregistration CI, and only then run the model once under the unchanged scoring and promotion thresholds.
