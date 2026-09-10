# Gate 1 Qualification and Empirical Status

Updated: 2026-09-10

## Gate-1 question

Gate 1 asks whether the Project Seed scaffold can make a fixed underlying model more capable on long-horizon/tool-using tasks under a controlled external resource envelope.

The scientific comparison is:

```text
same model artifact + same task family + same hard maximum budget

RAW ARM                         SEED ARM
model -> final answer           model -> planner -> tools -> observations
                                      -> critic -> replan -> final answer
```

The Seed arm must not quietly substitute a stronger model or receive an unbounded wallet.

## Infrastructure qualification

`seed gate1-certify` is a deterministic fail-closed canary validating the apparatus needed for real-model campaigns.

It checks that:
1. Raw and Seed declare the same provider identity;
2. both arms receive exactly the same resource envelope;
3. both stay inside that envelope;
4. Seed can complete a planted multi-step tool task;
5. the harness detects a planted capability difference;
6. non-allowlisted tools are rejected;
7. malformed model JSON fails closed;
8. hard model/token/tool budgets stop runaway execution;
9. exhaustion becomes an explicit terminal state;
10. model calls and paired evidence are content-hashed.

This deterministic canary qualifies the apparatus, not the empirical capability claim.

## Current real-model implementation

Gate 1 now also includes:
- local Ollama provider support;
- exact local model digest attestation;
- Raw single-call bounded-analysis protocol;
- deterministic relevant-tool routing for Seed;
- exact shortest-path, DAG critical-path, CRT, semantic transaction/reconciliation, record-aggregation, finite/assignment-CSP, exact Python-trace and constrained subset-optimization tools;
- sandboxed `python_compute` fallback;
- evidence-only critic requiring verified candidate answers;
- per-purpose output caps inside a common hard total budget;
- atomic per-pair checkpointing/resume;
- progress telemetry separated from transcript hashes;
- Seed implementation digest attestation;
- external-key scoring and paired bootstrap comparison.

## Hard resource envelope used for local holdout v2

Both arms were bounded by:
- max steps: 8;
- max model calls: 12;
- max tool calls: 8;
- max total tokens: 8000;
- max model/API cost: USD 0;
- temperature: 0;
- context: 4096;
- Raw/planner per-call output cap: 768;
- critic per-call output cap: 128.

Raw used one direct model call and no tools. Seed could distribute the same hard total envelope across planner/tool/critic iterations.

## Empirical campaigns completed

### Development/calibration campaign

An 8-task local Qwen3-8B campaign produced Raw 2/8 vs Seed 4/8, a +25 percentage-point observed gain. Strict Seed win rate was 50% and the paired confidence interval crossed zero. This did not satisfy promotion and the suite was retired to development use.

### Preregistered local holdout v2

A new 16-task private holdout was generated, independently audited for exact-answer correctness and uniqueness where applicable, and hashed before inference.

Preregistration commit: `8f38b01604964b1e6aabbef10d842051c52fb25c`.

Frozen candidate source: `8c18f91ad72c31007243e4bf2b8388b1421efd00`.

Model: local `qwen3:8b`, digest `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`.

Private task-suite SHA-256: `e44d93fcc949d4d43750b3feca3175039e65019c43e21140aaeb758625763411`.

Private answer-key SHA-256: `b86ed624705a7b68bcc1136cf77fd30058f7537969a1f24e42647b30b3b55b18`.

Final corrected result:
- Raw: **1/16 = 6.25%**;
- Seed: **5/16 = 31.25%**;
- mean gain: **+25 percentage points**;
- strict Seed win rate: **31.25%**;
- 95% paired-bootstrap CI for gain: **[0.00, 0.50]**.

Frozen empirical promotion requirements were:
- >=16 valid pairs;
- mean gain >=5 percentage points;
- strict Seed win rate >=60%;
- CI lower bound >0;
- no integrity or resource-envelope violation.

Pair count and mean gain passed. Win rate and CI did not. **Gate 1 is therefore NOT empirically certified.**

The complete result/audit record is [`GATE1_LOCAL_HOLDOUT_V2_RESULT.md`](GATE1_LOCAL_HOLDOUT_V2_RESULT.md).

## Scoring-system correction

After the 16-pair model run had fully completed and sealed, the first scoring pass exposed evaluator parsing bugs: a single accepted string was treated as a character iterable, and `FINAL:` prefixes in answer keys were not normalized like model output prefixes.

The frozen candidate/model run, tasks, answer key and evidence were not altered. The scoring implementation was corrected with regression tests, and the same sealed hashes were rescored. Local repository validation then passed **121/121 tests**.

This incident is retained as part of the audit trail rather than hidden because evaluator correctness is part of Gate 0/1 trustworthiness.

## Current empirical history through holdout v4

Holdout v3 used candidate `83ec193d6300b0658af8d4d3c45109880b28363f` and produced Raw **3/16** vs Seed **11/16**, +50 pp gain, CI **[+18.75 pp, +81.25 pp]**, but only **9/16 = 56.25%** strict Seed wins. It failed promotion and is retired development evidence.

Post-v3 reliability development produced candidate `b4242af758b1222f8ecea0bf7306e917a36ed9d8`, implementation digest `f9d882e185b235d0a8345640ee1577edb518be96dbf8af0f6b50ec204f5a1358`, with **134/134** local tests and **10/10** deterministic Gate-1 checks.

Holdout v4 was generated after that freeze, independently audited 16/16, and preregistered at `e346ffabb2f77bded32d29e58e8009dc2731fd20`. The sealed campaign produced Raw **3/16 (18.75%)** vs Seed **11/16 (68.75%)**, +50 pp gain, 95% CI **[+25.00 pp, +75.00 pp]**, and **8/16 = 50.00%** strict Seed wins. All criteria except the >=60% strict-win threshold passed, so Gate 1 remains **NOT empirically certified**.

Full audits: [`GATE1_LOCAL_HOLDOUT_V3_RESULT.md`](GATE1_LOCAL_HOLDOUT_V3_RESULT.md) and [`GATE1_LOCAL_HOLDOUT_V4_RESULT.md`](GATE1_LOCAL_HOLDOUT_V4_RESULT.md).

## Failure semantics

The bounded agent converts failures into explicit states:
- `budget_exhausted` for hard resource-limit violations;
- `blocked` for denied actions such as non-allowlisted tools;
- `failed` for malformed/unhandled provider/component errors.

A failed planner/critic/tool path cannot silently become a successful answer.

## What remains for Gate-1 empirical certification

Holdouts v2, v3 and v4 are retired development evidence and may not be reused as fresh certification sets.

v4 independently reproduces a large and statistically positive scaffold effect, but Gate 1 intentionally also requires broad paired reliability. Its 8/16 strict Seed wins remain below the frozen 60% threshold, even though pair count, mean gain, confidence interval, identity/integrity and resource criteria passed.

The next candidate may use v4 only to diagnose generic remaining failure and budget-exhaustion classes. It must then be frozen before a new private holdout v5 is generated, independently audited and preregistered. Gate 1 remains failed until a campaign satisfies every frozen criterion; the 50.00% v4 win rate is not rounded up or treated as equivalent to 60%.

## Storage policy

Canonical project state stays in GitHub: `sampathkumar-co/asi`.

Private holdout tasks, answer keys, raw evidence and signing material remain outside source control. GitHub stores code, documentation, public hashes and sanitized score summaries only.
