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

## Current vNext candidate

After holdout v2 was retired to development use, the observed failure classes were addressed generically. The resulting candidate is frozen at source commit `83ec193d6300b0658af8d4d3c45109880b28363f` with Seed implementation digest `a82be2b8cd2a60e4fa4021a0d6bfa0434c73032afbf0ec29771626385dccd708`.

The candidate passes **131/131** local regression tests and **10/10** deterministic Gate-1 infrastructure canaries. Development-only probes on retired H01-H16 cases verify the new transaction/reconciliation, exact Python-trace, subset-optimization and output-finalization paths. This is not promotion evidence. See [`GATE1_VNEXT_DEVELOPMENT.md`](GATE1_VNEXT_DEVELOPMENT.md).

The next certification attempt must use a new private holdout v3 generated and preregistered after this candidate identity was frozen.

## Failure semantics

The bounded agent converts failures into explicit states:
- `budget_exhausted` for hard resource-limit violations;
- `blocked` for denied actions such as non-allowlisted tools;
- `failed` for malformed/unhandled provider/component errors.

A failed planner/critic/tool path cannot silently become a successful answer.

## What remains for Gate-1 empirical certification

The H01-H16 holdout is now development evidence and may not be reused as a fresh certification set.

The next candidate must address the observed unseen weaknesses generically, then be frozen before a new private holdout is generated and audited. The next promotion attempt must again use a new preregistered task/key pair and must retain the same or explicitly preregistered promotion criteria.

Gate 1 will remain failed until a campaign actually satisfies those criteria. Positive individual task wins or a positive mean delta alone are not enough.

## Storage policy

Canonical project state stays in GitHub: `sampathkumar-co/asi`.

Private holdout tasks, answer keys, raw evidence and signing material remain outside source control. GitHub stores code, documentation, public hashes and sanitized score summaries only.
