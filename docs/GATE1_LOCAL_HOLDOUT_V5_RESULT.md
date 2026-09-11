# Gate 1 Local Holdout v5 Result

Date: 2026-09-10

Status: **COMPLETED — PROMOTION PASS**

This report records the preregistered Gate-1 v5 campaign exactly as run. It is the first campaign to satisfy every frozen Gate-1 promotion criterion.

## Frozen identities

- Seed source commit: `c34e1cd31c61efebc513f289ba9ac11cdd4412d0`
- Seed implementation digest: `011881547d85a31cccc3bd66a174e7ae9b3e8506014a6c918d248e78708e286c`
- Preregistration commit: `857aa0f4cac7437deb86646e6f72d682b16d806a`
- Model: local `qwen3:8b`
- Model digest: `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`
- Private task-suite SHA-256: `0e51dd6b8dc99e0e68589894b457fe5b80e98ea7815aeeb282cb25df5cf03b5b`
- Private answer-key SHA-256: `b86e19c1447f7556ecb2192e01889abdcf8dcc7704d2cd97c8bac1ae34784ad1`

The private task/key contents remain outside source control. The suite was independently reproduced and audited **16/16** before the first model inference.

## Evidence integrity

The completed evidence contains exactly 16 unique paired tasks, `X501` through `X516`. All pair hashes and the campaign content hash recomputed successfully after the run.

- campaign content hash: `7c3781d19220bcf0d2701e670c586c2a681e9d7b0624c1b0c5c24aa32db6c419`
- sealed evidence file SHA-256: `2464b0cc991369c2e12f16a57626a76c487617eda6fb1dc784895276432b3e96`
- Raw terminal status: 16 `succeeded`
- Seed terminal status: 15 `succeeded`, 1 `budget_exhausted`
- Raw max tokens: `633 / 8000`
- Seed max tokens: `7937 / 8000`
- Raw max model calls: `1 / 12`
- Seed max model calls: `7 / 12`
- Seed max tool calls: `4 / 8`
- no model/provider/implementation mismatch was detected
- no pair exceeded model-call, tool-call, step, token, or cost limits

GitHub Actions CI #145 passed for the frozen source candidate, #146 passed for its documentation freeze, and #147 passed for the preregistration commit. Local validation before the campaign was **140/140 tests PASS** with deterministic Gate-1 qualification **10/10 PASS**.

## Final score

Using the repository exact-answer scorer and the same paired-bootstrap procedure:

| Metric | Raw | Seed / delta |
|---|---:|---:|
| Correct | 1/16 | **15/16** |
| Accuracy | 6.25% | **93.75%** |
| Mean capability gain | — | **+87.50 percentage points** |
| Strict Seed win rate | — | **14/16 = 87.50%** |
| 95% paired-bootstrap CI for gain | — | **[+68.75 pp, +100.00 pp]** |

Paired outcome counts:

- Seed-only correct: **14**
- Raw-only correct: **0**
- both correct: **1**
- both wrong: **1**

Public score-only artifact: [`../artifacts/gate1-local-holdout-v5-score.json`](../artifacts/gate1-local-holdout-v5-score.json).

Score report content hash: `0a18148a326503edf14e3cf4fbbce159ee6429aee641a33bdb19a2a4ef0fc9c1`.
Original private score-file SHA-256 (Windows CRLF bytes): `8c2a8dfcb7ccb05848dc205c4884a893f3a841939718bb2a1ab7c372ab8551b5`.
Public GitHub score-artifact SHA-256 (LF-normalized bytes, identical JSON values): `26958d11195b9ca6662b9ce64839418ed61e1cf8977ab31992ececa0939f64cd`.

## Frozen promotion decision

| Criterion | Requirement | v5 | Verdict |
|---|---:|---:|---|
| Valid paired tasks | >=16 | 16 | PASS |
| Mean Seed gain | >=5 pp | +87.50 pp | PASS |
| Strict Seed win rate | >=60% | 87.50% | PASS |
| Bootstrap CI lower bound | >0 | +68.75 pp | PASS |
| Identity/integrity | no mismatch | clean | PASS |
| Resource envelope | no violation | clean | PASS |

**Gate 1 promotes.** v5 satisfies every preregistered criterion without changing the candidate, model, tasks, key, budgets, scorer, or thresholds after inference began.

## Per-task score-only audit

| Task | Raw | Seed |
|---|---:|---:|
| X501 | 1 | 1 |
| X502 | 0 | 1 |
| X503 | 0 | 1 |
| X504 | 0 | 1 |
| X505 | 0 | 1 |
| X506 | 0 | 1 |
| X507 | 0 | 1 |
| X508 | 0 | 1 |
| X509 | 0 | 1 |
| X510 | 0 | 0 |
| X511 | 0 | 1 |
| X512 | 0 | 1 |
| X513 | 0 | 1 |
| X514 | 0 | 1 |
| X515 | 0 | 1 |
| X516 | 0 | 1 |

No private task prompt or accepted answer text is published here.

## Interpretation

v5 provides the first promotion-grade Gate-1 result: under the same local Qwen3-8B artifact and hard resource envelope, Seed raises exact-answer accuracy from 6.25% to 93.75%, wins 14 pairs that Raw loses, and has a paired-bootstrap interval entirely above zero.

This establishes the bounded fixed-model scaffold result required by Gate 1. It does **not** establish AGI, ASI, recursive amplification, or autonomous self-improvement. Those are later-gate questions.

Holdout v5 is now retired evidence and must never be reused as fresh certification data. The active empirical program moves to **Gate 2: scientific-method workflow and adversarial/independent verification**.