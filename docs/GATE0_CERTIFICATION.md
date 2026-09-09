# Gate 0 Certification Record

**Gate:** 0 — Evaluation / Measurement Infrastructure  
**Status:** COMPLETE — infrastructure qualification passed  
**Date:** 2026-09-09  
**Qualification implementation commit:** `ac34eb02dbebd4271493f28f259b849b259bacc7`  
**GitHub Actions run:** `34358682691`  
**CI result:** success on Python 3.11, 3.12 and 3.13

## What "Gate 0 complete" means

Gate 0 is the measurement foundation. Completion means Project Seed now has a fail-closed evaluator capable of separating candidate code from private evaluation data, measuring repeated outcomes and resource use, detecting evaluator mutation, signing/verifying receipts, rejecting tampered evidence, and producing a machine-readable qualification certificate.

It does **not** mean a frontier model has demonstrated recursive amplification. That is a later empirical claim. Gate 0 exists so future claims can be measured without moving the goalposts.

## CI evidence

Python 3.12 qualification run:

- **46/46 automated tests passed**;
- `seed gate0-certify` exited successfully;
- machine-readable certificate reported `passed: true`;
- certificate artifact uploaded by GitHub Actions;
- certificate content hash: `50525116d5b3431453b12391cce421485f192544ee85d698e6eb142c49ae55d1`;
- evaluator digest before: `8c6dcd69292797ede6d661c858d9ffb051a6af7981a5410a160372b74d3292bf`;
- evaluator digest after: `8c6dcd69292797ede6d661c858d9ffb051a6af7981a5410a160372b74d3292bf`;
- evaluator files covered: 24;
- signed receipts verified: 15.

## Qualification checks

All checks passed:

1. `private_holdouts_external`
2. `known_good_passes_hidden`
3. `known_good_passes_ood`
4. `known_bad_fails_closed`
5. `all_receipts_signed_and_verified`
6. `tampered_signature_rejected`
7. `paired_statistics_discriminate`
8. `evaluator_unchanged_during_qualification`

The known-good canary scored 1.0 with a 95% CI of `[1.0, 1.0]` on both private and OOD qualification suites. The known-bad canary scored 0.0 with a 95% CI of `[0.0, 0.0]`. The paired bootstrap discrimination canary produced a mean gain and confidence interval of `1.0`.

## Gate-0 capabilities now available

### Evaluation
- bounded scorer abstraction;
- exact and numeric scorers;
- external private-holdout loading;
- OOD suite loading;
- repeated evaluation;
- score confidence summaries;
- paired bootstrap comparisons.

### Provenance / integrity
- SHA-256 evaluation receipts;
- HMAC-SHA256 trusted-control-plane receipt signing;
- constant-time signature verification;
- evaluator-tree SHA-256 snapshots;
- before/after immutability verification;
- append-only per-run event hash chain.

### Resource accounting
Measured candidate outputs can attach externally observed:
- model calls;
- tool calls;
- input/output tokens;
- API cost;
- human interventions;
- compute seconds;
- wall-clock duration.

These values are carried into `RunMetrics` and the evaluation receipt so a candidate cannot be called better merely because it consumed unrecorded extra resources.

## Reproduce

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
seed gate0-certify --repo-root . --output artifacts/gate0-certificate.json
```

A non-passing qualification returns a non-zero exit code.

## Remaining research, moved beyond Gate 0

The following are intentionally **not required to call the measurement infrastructure complete**:

- integrating a live frontier LLM;
- comparing a raw model with the Seed scaffold;
- proving improvement on substantive private multi-domain benchmarks;
- demonstrating metaproductivity or recursive amplification.

Those are empirical Gate-1-and-later experiments performed *using* the Gate-0 evaluator.
