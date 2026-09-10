# Gate 1 Local Holdout v3 Result

Date: 2026-09-10

Status: **COMPLETED — PROMOTION FAIL**

This report records the preregistered Gate-1 v3 campaign exactly as run. The result is published even though promotion failed, as required by the preregistration.

## Frozen identities

- Seed source commit: `83ec193d6300b0658af8d4d3c45109880b28363f`
- Seed implementation digest: `a82be2b8cd2a60e4fa4021a0d6bfa0434c73032afbf0ec29771626385dccd708`
- Preregistration commit: `f10457f41d167551657e7e0e2b7741f79ed25b7b`
- Model: local `qwen3:8b`
- Model digest: `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`
- Private task-suite SHA-256: `904cb39ea0a06a276c2ee351618f3cf30ec6a83b41cdb13b0ac757a351c961f2`
- Private answer-key SHA-256: `cdf0879ab3fb166ef4d16cd830c2f2fd7d5ef469db1b1dbf1d89376fa9f61258`

The private task/key contents remain outside source control.

## Evidence integrity

The completed evidence contains exactly 16 unique paired tasks, `V301` through `V316`. All pair hashes and the campaign content hash recomputed successfully before scoring.

- campaign content hash: `2103c567d92d4796819671e32c3000f3b74e234fcd369f11ed9a07061661dba6`
- sealed evidence file SHA-256: `e4efeaede8623344d9de5019a86b1ad096f973706c5156633f3dd5f714c0f871`
- Raw terminal status: 16 `succeeded`
- Seed terminal status: 12 `succeeded`, 4 `budget_exhausted`
Every Raw/Seed pair used the same declared hard envelope. Maximum observed usage remained within it:

- Raw max tokens: `557 / 8000`
- Seed max tokens: `7446 / 8000`
- no model/provider/implementation mismatch was detected
- no pair exceeded model-call, tool-call, step, token, or cost limits

## Final score

Using exact-answer scoring and a 4,000-sample paired bootstrap (`seed=0`):

| Metric | Raw | Seed / delta |
|---|---:|---:|
| Correct | 3/16 | **11/16** |
| Accuracy | 18.75% | **68.75%** |
| Mean capability gain | — | **+50.00 percentage points** |
| Strict Seed win rate | — | **9/16 = 56.25%** |
| 95% paired-bootstrap CI for gain | — | **[+18.75 pp, +81.25 pp]** |

Paired outcome counts:

- Seed-only correct: **9**
- Raw-only correct: **1**
- both correct: **2**
- both wrong: **4**

Public score-only artifact: [`../artifacts/gate1-local-holdout-v3-score.json`](../artifacts/gate1-local-holdout-v3-score.json).

Score report content hash: `b9029ad107cd3467977cf1c3b88bcf6504a2a6ef5b280f47f1b3a1b0704fe8f4`.
## Frozen promotion decision

The preregistered promotion rule required all criteria below:

| Criterion | Requirement | v3 | Verdict |
|---|---:|---:|---|
| Valid paired tasks | >=16 | 16 | PASS |
| Mean Seed gain | >=5 pp | +50 pp | PASS |
| Strict Seed win rate | >=60% | 56.25% | **FAIL** |
| Bootstrap CI lower bound | >0 | +18.75 pp | PASS |
| Identity/integrity | no mismatch | clean | PASS |
| Resource envelope | no violation | clean | PASS |

**Gate 1 does not promote.** The experiment misses only the frozen strict-win criterion. With 16 pairs, the threshold requires at least 10 strict Seed wins; v3 produced 9. The threshold is not weakened after observing the result.

## Per-task score-only audit

| Task | Raw | Seed |
|---|---:|---:|
| V301 | 0 | 0 |
| V302 | 0 | 0 |
| V303 | 0 | 1 |
| V304 | 0 | 1 |
| V305 | 1 | 1 |
| V306 | 0 | 1 |
| V307 | 0 | 1 |
| V308 | 0 | 1 |
| V309 | 1 | 0 |
| V310 | 0 | 0 |
| V311 | 0 | 1 |
| V312 | 0 | 1 |
| V313 | 0 | 1 |
| V314 | 0 | 1 |
| V315 | 0 | 0 |
| V316 | 1 | 1 |

No task prompt or answer text is published here.

## Scoring-container compatibility note

The preregistered v3 answer-key file is a bare `{task_id: accepted_answer}` JSON mapping. The repository's CLI scorer expects a wrapper object containing `suite_id` and `answers`. This container mismatch was discovered only after the campaign had fully sealed and before any score was computed.

The preregistered answer-key bytes were **not modified**. A read-only scoring adapter verified the exact preregistered SHA-256, supplied the already-sealed suite ID as metadata, and then used the repository's existing `score_answer()` canonicalization plus `paired_bootstrap(..., samples=4000, seed=0)`. No model output, task, accepted answer, threshold, or scoring semantics were altered.

Future holdouts should standardize the private answer-key container before preregistration so the normal CLI scorer can consume the file directly.

## Interpretation

v3 is substantially stronger than v2: Seed accuracy increased to 68.75%, the Raw-to-Seed gain doubled to +50 percentage points, and the bootstrap interval now clears zero. This is meaningful evidence that the frozen scaffold improves the fixed local model on this holdout.

It is still not enough for Gate-1 certification because the project intentionally requires broad paired reliability, not just aggregate accuracy gain. One Raw-only win plus four both-wrong cases leave the strict Seed win count at 9 rather than the required 10.

After publication, v3 becomes retired development evidence. It must not be reused as fresh certification data for another promotion claim.
