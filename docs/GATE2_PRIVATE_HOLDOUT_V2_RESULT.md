# Gate 2 Private Holdout v2 - Result

Updated: 2026-09-12

## Outcome

**Gate 2 v2 does not promote.** This preregistered private/OOD campaign is immutable failed certification evidence.

Frozen candidate commit: `261cc0d486830b3219a58d499661ccf1c7f1327b`.

Preregistration commit: `f7a461881e691640f0a822548bd39de473ef2536`.

Candidate implementation digest: `d8a028f394121ca3dc6e5c890304bd3d13cd03e5566467befecb31190540b340`.

Model: `qwen3:8b`, manifest SHA-256 `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`.

Both freeze and preregistration commits passed GitHub Actions before inference began.

## Frozen private identities

- suite: `gate2-private-holdout-v2`
- paired tasks: **18**; label balance **H1=6, H2=6, H3=6**
- task SHA-256: `98432c2baf6be32ed5a6245458f61e54655e2afe46dd82be066306adf0f453e0`
- answer-key SHA-256: `0201a17e96606c203f0bb464ea098cbb2216fb22025e370bcfa4f293c4c239b5`
- audit SHA-256: `4ee584610f368e87ac4fcd65f511204e650359c3c7428c6b8d11ab8bc0b8206f`
- maximum old-question fuzzy similarity: **0.6108** after pre-inference overlap filtering

## Sealed evidence identities

- evidence file SHA-256: `ceb466aecc9b20a13c9e21e92c9a1128fb7ded1f25a68963bec88c2d8214cc4a`
- evidence content hash: `bc02482f44b245b6d325e7da75b69f89f152ab3810895aa0d171004f0a8c7510`
- score file SHA-256: `1962331a2d9cbb581590619f206d25e01997576086a6d2cd64eca925e3cfc738`
- score content hash: `bc0082182505f7e2af07b33c93a85863b723bd1ab3b774b38f7ff820f4f4f940`

All **18/18** pairs validated before scoring. Every Seed arm stayed within the frozen 16-call / 16-step / 15,000-token / zero-tool envelope and used zero repair calls.

## Aggregate result

- valid pairs: **18**
- Raw mean: **0.81250**
- Seed mean: **0.82083**
- mean Seed-minus-Raw gain: **+0.00833**
- strict Seed wins: **6/18 = 33.33%**
- paired outcomes: **6 wins / 7 losses / 5 ties**
- paired-bootstrap 95% CI: **[-0.07361, +0.09583]**
- Seed verifier acceptance: **16/18 = 88.89%**
- Raw correct final hypotheses: **16/18**
- Seed correct final hypotheses: **16/18**

## Frozen promotion checks

- valid pairs >=16: **PASS**
- Seed mean >=0.75: **PASS**
- mean gain >=0.15: **FAIL**
- strict win rate >=60%: **FAIL**
- bootstrap lower bound >0: **FAIL**
- verifier acceptance >=75%: **PASS**
- identity/integrity/resource/protocol checks: **PASS**

Because the promotion rule is conjunctive, `promotion_pass=false`.

## Per-task numeric result

| Task | Raw | Seed | Delta | Verifier accepted |
|---|---:|---:|---:|:---:|
| V2P01_THERMAL | 0.925 | 0.900 | -0.025 | yes |
| V2P02_FERMENT | 0.775 | 0.850 | +0.075 | yes |
| V2P03_PACKET | 0.850 | 0.850 | +0.000 | yes |
| V2P04_SOLAR | 1.000 | 0.750 | -0.250 | yes |
| V2P05_BUILD | 0.925 | 0.675 | -0.250 | yes |
| V2P06_REAGENT | 0.900 | 0.900 | +0.000 | no |
| V2P07_GREENHOUSE | 0.775 | 0.500 | -0.275 | no |
| V2P08_PICKING | 0.000 | 0.275 | +0.275 | yes |
| V2P09_TRACE | 0.775 | 0.850 | +0.075 | yes |
| V2P10_INFERENCE | 1.000 | 0.900 | -0.100 | yes |
| V2P11_REPLICA | 0.750 | 0.750 | +0.000 | yes |
| V2P12_ROBOT | 0.925 | 0.925 | +0.000 | yes |
| V2P13_CONCRETE | 0.750 | 1.000 | +0.250 | yes |
| V2P14_CONVERSION | 0.350 | 0.825 | +0.475 | yes |
| V2P15_TRANSIENT | 1.000 | 0.925 | -0.075 | yes |
| V2P16_DEDUP | 1.000 | 0.900 | -0.100 | yes |
| V2P17_CONTAINER | 0.925 | 1.000 | +0.075 | yes |
| V2P18_PURIFY | 1.000 | 1.000 | +0.000 | yes |

## Diagnostic interpretation

V2 fixed the dominant verifier false-negative problem seen in private v1: verifier acceptance rose from **50%** to **88.89%** without lowering the frozen 75% threshold. However, that verifier improvement did **not** translate into the required task-level advantage over Raw.

Raw and Seed were each correct on 16/18 final hypotheses. The high Raw mean (**0.81250**) left little aggregate margin, and Seed produced only six strict wins while losing seven pairs. The scientific-method scaffold therefore did not demonstrate the preregistered incremental capability gain on this holdout.

Two Seed final hypotheses were wrong: `V2P07_GREENHOUSE` and `V2P08_PICKING`. `V2P07_GREENHOUSE` was verifier-rejected, while `V2P08_PICKING` was verifier-accepted. The latter is a concrete remaining false-acceptance case for future development diagnostics.

No threshold, scorer, prompt, task, answer key, resource limit, or candidate source was changed after private inference began.

## Retirement rule

This private-v2 holdout is now permanently retired. It may be used only for diagnostic analysis. Any later Gate-2 certification attempt must freeze a new candidate first and then use a completely new independently audited and preregistered private/OOD holdout.

Raw private tasks, observations, answer-key contents, and campaign evidence remain outside Git. Git contains only hashes, this audit record, and the sanitized numeric score artifact.
