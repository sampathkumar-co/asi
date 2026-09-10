# Gate 1 Local Holdout v4 Result

Date: 2026-09-10

Status: **COMPLETED — PROMOTION FAIL**

This report records the preregistered Gate-1 v4 campaign exactly as run. The result is published even though promotion failed, as required by the preregistration.

## Frozen identities

- Seed source commit: `b4242af758b1222f8ecea0bf7306e917a36ed9d8`
- Seed implementation digest: `f9d882e185b235d0a8345640ee1577edb518be96dbf8af0f6b50ec204f5a1358`
- Preregistration commit: `e346ffabb2f77bded32d29e58e8009dc2731fd20`
- Model: local `qwen3:8b`
- Model digest: `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`
- Private task-suite SHA-256: `a507c95ce85a0adef30f9bf217e49cb3e27824ddc1bd69aedb67d7c32f51b7ad`
- Private answer-key SHA-256: `f93e0aaeac12721882c37f2cca2f3f7b8ae28357793214d4c4ea8f4c91c96eac`

The private task/key contents remain outside source control. The v4 answer key used the repository scorer's native wrapper schema before preregistration.
## Evidence integrity

The completed evidence contains exactly 16 unique paired tasks, `W401` through `W416`. All pair hashes and the campaign content hash recomputed successfully before scoring.

- campaign content hash: `c3cfa3e2332d6ad4d54ac77ce294007f96cc6ce514a5cd3fd7e46d20b79d7e6f`
- sealed evidence file SHA-256: `70e1e027e41d1c0aa2c5bed8906a8e8a04ff1a71008c50dab0a818c2359270ed`
- Raw terminal status: 16 `succeeded`
- Seed terminal status: 13 `succeeded`, 3 `budget_exhausted`
- Raw max tokens: `565 / 8000`
- Seed max tokens: `7859 / 8000`
- no model/provider/implementation mismatch was detected
- no pair exceeded model-call, tool-call, step, token, or cost limits

Post-run repository validation remained green at **134/134 tests**, and the deterministic Gate-1 qualification remained **10/10 PASS** with content hash `357b3beac3bbcfb04ccf09b6e00a74dd7fdd95b2ef9ae72f7dd15fc9cff16799`.
## Final score

Using the repository's native exact-answer scorer and 4,000-sample paired bootstrap (`seed=0`):

| Metric | Raw | Seed / delta |
|---|---:|---:|
| Correct | 3/16 | **11/16** |
| Accuracy | 18.75% | **68.75%** |
| Mean capability gain | — | **+50.00 percentage points** |
| Strict Seed win rate | — | **8/16 = 50.00%** |
| 95% paired-bootstrap CI for gain | — | **[+25.00 pp, +75.00 pp]** |

Paired outcome counts:

- Seed-only correct: **8**
- Raw-only correct: **0**
- both correct: **3**
- both wrong: **5**

Public score-only artifact: [`../artifacts/gate1-local-holdout-v4-score.json`](../artifacts/gate1-local-holdout-v4-score.json).

Score report content hash: `8143ddeb19a76099feb4b54f911b01eeaa97c1c95d6f9b29f12e3d65f7ce7faa`.
Score file SHA-256: `064b9e9affc75262f30690961b35603b8d3760bba73bad276be23bfc06f24b86`.
## Frozen promotion decision

The preregistered promotion rule required every criterion below:

| Criterion | Requirement | v4 | Verdict |
|---|---:|---:|---|
| Valid paired tasks | >=16 | 16 | PASS |
| Mean Seed gain | >=5 pp | +50 pp | PASS |
| Strict Seed win rate | >=60% | 50.00% | **FAIL** |
| Bootstrap CI lower bound | >0 | +25.00 pp | PASS |
| Identity/integrity | no mismatch | clean | PASS |
| Resource envelope | no violation | clean | PASS |

**Gate 1 does not promote.** With 16 pairs the 60% threshold requires at least 10 strict Seed wins; v4 produced 8. The threshold is not weakened after observing the result.

Compared only at the aggregate-metric level, v4 matches v3's Raw/Seed accuracies and +50 pp gain, while its strict Seed win rate is lower (50.00% vs 56.25%). Because v3 and v4 use different unseen task instances, task-level outcomes are not treated as directly paired across campaigns.
## Per-task score-only audit

| Task | Raw | Seed |
|---|---:|---:|
| W401 | 0 | 0 |
| W402 | 0 | 1 |
| W403 | 0 | 0 |
| W404 | 0 | 0 |
| W405 | 0 | 1 |
| W406 | 0 | 1 |
| W407 | 0 | 1 |
| W408 | 0 | 1 |
| W409 | 1 | 1 |
| W410 | 1 | 1 |
| W411 | 0 | 1 |
| W412 | 0 | 0 |
| W413 | 0 | 0 |
| W414 | 0 | 1 |
| W415 | 1 | 1 |
| W416 | 0 | 1 |

No task prompt or accepted answer text is published here.
## Interpretation

v4 independently reproduces the large aggregate scaffold effect seen in v3: Seed reaches 68.75% accuracy versus Raw at 18.75%, with a +50 pp paired gain and a confidence interval entirely above zero.

That is still insufficient for Gate-1 promotion because the project also requires broad paired reliability. v4 achieves only 8 strict Seed wins, two below the minimum of 10 required by the frozen 60% rule.

After publication, v4 becomes retired development evidence. It must not be reused as fresh certification data. The next candidate may use v4 only to diagnose generic failure classes, then must face a newly generated, independently audited and preregistered holdout before another promotion claim.