# Gate 1 vNext Development Candidate

Updated: 2026-09-10

## Purpose

This document records post-holdout development performed after Gate-1 local holdout v2 failed its preregistered promotion rule.

The H01-H16 suite is **retired development evidence**. Results in this file are not fresh certification evidence and must not be used to promote Gate 1.

## Frozen vNext implementation

- source commit: `83ec193d6300b0658af8d4d3c45109880b28363f`
- Seed implementation digest: `a82be2b8cd2a60e4fa4021a0d6bfa0434c73032afbf0ec29771626385dccd708`
- implementation files attested: 27
- local validation: **131/131 tests passing** on Windows 11 / Python 3.13.15
- deterministic Gate-1 infrastructure canary: **10/10 checks passing**
- canary content hash: `2e05acf41f59fda7f753ebc7d516cbbc025feded613e09b9319315279dc0955f`

This candidate remains a Gate-1 candidate until it passes a new unseen preregistered holdout.
## Generic capability changes

The vNext candidate addresses failure classes observed on the retired v2 holdout without embedding task answers:

- semantic transaction/reconciliation tool with status filtering, sale math, discounts and add/subtract kinds;
- verbatim transaction-stream parsing to reduce record-identity transcription errors;
- exact safe Python trace execution using the supplied source rather than model-rewritten code;
- exhaustive constrained subset optimization with separate implication and mutual-exclusion semantics;
- deterministic routing to the new exact tools;
- verified-answer normalization for a checked answer that is missing only the `FINAL:` prefix;
- assignment rendering that defaults to concatenation for single-character order labels;
- stable calculator-only deterministic Gate-1 canary so registry growth cannot consume its small prompt budget.

The exact tools remain behind the same planner allowlist, hard budget and evidence-only critic boundary.

## Retired-holdout development probes

Development-only probes on the previously problematic classes showed verified one-step closure for:
- critical-path output finalization;
- semantic ledger arithmetic;
- single-letter ordering output;
- exact Python tracing;
- approved credit/debit reconciliation;
- constrained subset optimization;
- a second ordering/assignment case.
These checks demonstrate that the intended architectural fixes work on known development cases. They do **not** estimate unseen generalization because the cases were already observed before this candidate was built.

## Integrity boundary

- The v2 holdout result remains unchanged and failed promotion.
- Private holdout prompts, answer keys and raw evidence remain outside source control.
- The vNext candidate may not be modified during its next promotion campaign.
- A new private task/key suite must be generated only after this candidate identity is frozen.
- The new suite must be independently audited and preregistered before inference.
- Promotion thresholds must remain frozen or be explicitly preregistered before the run; they may not be weakened after observing results.

## Next empirical step

Gate 1 is now at **vNext candidate frozen / new-holdout preparation**.

The next promotion attempt is holdout v3:
1. generate materially new private tasks outside the repository;
2. independently verify answers and uniqueness/optimality where applicable;
3. preregister task/key hashes, candidate commit/digest, model digest, budgets and thresholds;
4. run Raw vs Seed pairs without architecture changes;
5. score once against the external key and publish the result whether it passes or fails.

Gate 2 remains blocked as a promotion stage until Gate 1 actually satisfies its empirical criteria.
