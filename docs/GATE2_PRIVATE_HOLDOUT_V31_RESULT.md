# Gate 2 Private Holdout v3.1 - Result

Updated: 2026-09-13

## Outcome

**Gate 2 v3.1 does not promote.** The preregistered private/OOD campaign completed all 18 pairs, but the frozen mean-gain criterion failed. One Raw arm also suffered a confirmed local Ollama/CUDA infrastructure failure, so this holdout is retired and must not be reused as fresh certification evidence.

Frozen candidate commit: `2b98491641426f9ebe1678b8491a18a583e6c784`.

Preregistration commit: `393c22abf67e70675870f7f054eed023685cc08b`.

Candidate implementation digest: `c0abee591ed723a46ba57b527c2189efc0d711f3d3a423866a611503e8f16ce8`.

Model: `qwen3:8b`, manifest SHA-256 `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`.

Candidate CI #155 and preregistration CI #156 both completed successfully before private inference began.

## Frozen private identities

- suite: `gate2-private-holdout-v31`
- paired tasks: **18**; label balance **H1=6, H2=6, H3=6**
- task SHA-256: `408542488bc207f2d7b3f169ca4357e001e3cfded8872249ac17461bdf44f24a`
- answer-key SHA-256: `d7e104467cc80a472d60ba2a3de32c50c224d5c7d1f0c6a7918c1d3433d364f9`
- audit SHA-256: `431bc0e63e35a45d9a1db41cbe408cd256959ab54e9fcdb7f09552ed94ce0a14`
- maximum old-question fuzzy similarity: **0.696078 < 0.72**
## Sealed evidence identities

- evidence content hash: `4c39ef68987158aa43ff348b3369e8b8d2fdc25e0b5e312a73cc5f70f0db4181`
- evidence file SHA-256: `4c86cbfaa9882bd56a0b256d8b4685fb95a655ed02325704f10366e4d875e4a1`
- score content hash: `e6e773232c5a9f67f35167866ffdd680819e32a334b77196bfc374ca0d8533e9`
- external frozen score file SHA-256: `8575059981c5f28d215dde6e3aa6fccc43fd9423f99fd0120bf75d91ee14b8b0`
- normalized Git score artifact SHA-256: `530c8b965876ae110090675456a32f8816aa802c96d0cde68b517f5bf922ae9a`

All 18 pair records sealed under the frozen candidate/model/settings. Seed normally used six calls and stayed below 8,200 tokens. `V31P06_PRINT` used one bounded repair and then failed closed. No arm exceeded the 16-call / 16-step / 15,000-token / zero-tool envelope.

## Frozen aggregate score

- valid pairs reported by the frozen scorer: **18**
- Raw mean: **0.78750**
- Seed mean: **0.93472**
- mean Seed-minus-Raw gain: **+0.14722**
- strict Seed wins: **14/18 = 77.78%**
- paired outcomes: **14 wins / 1 loss / 3 ties**
- paired-bootstrap 95% CI: **[+0.01806, +0.28472]**
- Seed verifier acceptance: **15/18 = 83.33%**
- Raw correct final hypotheses: **14/18**
- Seed correct final hypotheses: **17/18**

The frozen scorer therefore returns `promotion_pass=false` because mean gain is below the preregistered **+0.15000** threshold.
## Infrastructure incident

`V31P01_CORROSION` Raw failed before any model-call record was emitted: status `failed:RuntimeError`, model calls **0**, tokens **0**. The sealed progress journal contains no Raw call for that arm.

Ollama server logs identify the cause at 2026-09-13 20:16:32 +05:30: the first `/api/chat` returned HTTP **500** after the CUDA llama-server crashed during warm-up with `CUDA error: shared object initialization failed` and process exit `0xc0000409`. Ollama then restarted the model and subsequent calls proceeded normally.

This is an infrastructure failure, not evidence that Raw reasoned incorrectly. The frozen scorer nevertheless fail-closes the Raw arm to score 0.000, because that was the frozen runtime behavior. That score is preserved and is not edited post hoc.

The incident does **not** rescue promotion. The failed Raw arm contributes a +1.000 delta in Seed's favor, so it can only inflate the observed mean gain. Removing this contaminated pair as a diagnostic sensitivity check leaves 17 pairs with Raw **0.83382**, Seed **0.93088**, gain **+0.09706**, strict wins **13/17 = 76.47%**, verifier acceptance **14/17 = 82.35%**, and a 4,000-sample paired-bootstrap CI of **[-0.00882, +0.19265]**. This sensitivity analysis is not a replacement score; it only shows that the certification failure is robust to the incident.

For future campaigns, provider/transport failures must be distinguished from model/protocol failures before certification scoring, and the exact exception message must be preserved in sealed telemetry.

## Other failure-mode audit

`V31P06_PRINT` Seed is a genuine protocol/model failure. Its initial attribution violated the frozen completeness rule (`attribution must cover every declared outcome exactly once`); the one allowed bounded repair also failed validation, so the arm correctly failed closed with status `failed:ValueError`.

`V31P16_MRI` and `V31P17_COMPRESSOR` completed successfully and both verifiers returned semantic `pass` verdicts, but adversarial confidence was **0.74118** and **0.76000**, below the frozen **0.80** acceptance threshold. Their verifier rejections are therefore expected protocol behavior, not infrastructure defects.
## Frozen promotion checks

- valid pairs >=16: **PASS** under the frozen scorer
- Seed mean >=0.75: **PASS**
- mean gain >=0.15: **FAIL** (`0.14722`)
- strict win rate >=60%: **PASS**
- bootstrap lower bound >0: **PASS** under the frozen score
- verifier acceptance >=75%: **PASS**
- candidate/model/task/key/resource identities: **PASS**
- clean certification-quality execution: **FAIL** because one Raw arm was contaminated by a confirmed Ollama/CUDA transport failure

Gate 2 therefore remains **NOT EMPIRICALLY CERTIFIED**. The numerical failure alone is sufficient; the infrastructure incident is an additional reason not to promote from this campaign.

## Per-task numeric result

| Task | Raw | Seed | Delta | Verifier accepted | Note |
|---|---:|---:|---:|:---:|---|
| V31P01_CORROSION | 0.000 | 1.000 | +1.000 | yes | Raw infrastructure failure |
| V31P02_BEAMFORM | 1.000 | 1.000 | +0.000 | yes | |
| V31P03_CERAMIC | 1.000 | 1.000 | +0.000 | yes | |
| V31P04_ORBIT | 0.825 | 0.900 | +0.075 | yes | |
| V31P05_FISH | 0.900 | 1.000 | +0.100 | yes | |
| V31P06_PRINT | 0.525 | 0.000 | -0.525 | no | Seed attribution repair failed closed |
| V31P07_DESICCANT | 0.825 | 1.000 | +0.175 | yes | |
| V31P08_INTERFERO | 0.900 | 1.000 | +0.100 | yes | |
| V31P09_AERATION | 0.500 | 1.000 | +0.500 | yes | |
| V31P10_ROUTE | 0.900 | 1.000 | +0.100 | yes | |
| V31P11_DISSOLVE | 0.900 | 1.000 | +0.100 | yes | |
| V31P12_PHISH | 0.900 | 1.000 | +0.100 | yes | |
| V31P13_WINGLET | 0.925 | 1.000 | +0.075 | yes | |
| V31P14_SEISMIC | 0.825 | 1.000 | +0.175 | yes | |
| V31P15_DYE | 1.000 | 1.000 | +0.000 | yes | |
| V31P16_MRI | 0.900 | 1.000 | +0.100 | no | adversarial confidence <0.80 |
| V31P17_COMPRESSOR | 0.425 | 0.925 | +0.500 | no | adversarial confidence <0.80 |
| V31P18_DRONE | 0.925 | 1.000 | +0.075 | yes | |

## Interpretation

V3.1 transferred much better than private v2 and largely fixed the probability-collision architecture that failed in v3. Seed reached **0.93472**, won 14/18 frozen-score pairs, and retained verifier acceptance above threshold. However, the preregistered question is not whether the candidate looks promising; it is whether every frozen promotion condition passes on clean private evidence.

It does not. Even the frozen score, which gives Seed the full benefit of the contaminated Raw zero, misses the mean-gain threshold by **0.00278**. Removing the contaminated pair lowers the observed gain substantially. Thresholds are therefore not weakened and this holdout is not rerun.

The main next-cycle engineering targets are now narrow and evidence-backed: make provider failures explicit and campaign-invalidating rather than silently score-like; preserve exception details in sealed telemetry; improve attribution completeness/repair reliability; and improve verifier confidence calibration without lowering the 0.80 rule.

## Retirement rule

This v3.1 private holdout is permanently retired. It may be used only for diagnostic analysis. Any future Gate-2 certification attempt must first freeze a new candidate, harden infrastructure-failure handling, pass deterministic qualification and CI, then use a completely new independently audited and preregistered private/OOD holdout.

Raw private tasks, observations, answer-key contents, raw evidence, progress telemetry, and local Ollama logs remain outside Git. Git contains only hashes, sanitized numeric score data, and this audit/result record.

Sanitized score artifact: [`../artifacts/gate2-private-holdout-v31-score.json`](../artifacts/gate2-private-holdout-v31-score.json).
