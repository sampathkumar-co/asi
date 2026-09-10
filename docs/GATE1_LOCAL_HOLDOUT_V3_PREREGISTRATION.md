# Gate 1 Local Holdout v3 Preregistration

Date: 2026-09-10

Status: **FROZEN BEFORE MODEL INFERENCE**

This document preregisters the next Project Seed Gate-1 local promotion attempt. The private task suite and answer key remain outside source control. Only their hashes, audit status, candidate/model identities, resource envelope, and promotion rules are public here.

## Frozen candidate

- Seed source commit: `83ec193d6300b0658af8d4d3c45109880b28363f`
- Seed implementation digest: `a82be2b8cd2a60e4fa4021a0d6bfa0434c73032afbf0ec29771626385dccd708`
- Local validation before preregistration: **131/131 tests passing**
- Deterministic Gate-1 canary before preregistration: **10/10 checks passing**
- Canary content hash: `2e05acf41f59fda7f753ebc7d516cbbc025feded613e09b9319315279dc0955f`
- GitHub CI run #138 on documentation head `9ca5546c84581f42b143d888bbe57476ea3756ed`: **success**

No Seed architecture changes are permitted after the first holdout-v3 model inference if the campaign is to count toward promotion.

## Frozen model

- Provider: local Ollama
- Model name: `qwen3:8b`
- Exact model digest: `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`
- Temperature: `0`
- Context window used by campaign: `4096`
- Internal thinking mode: disabled

Raw and Seed must use the exact same local model artifact.

## Private holdout identity

- Suite ID: `gate1-local-holdout-v3`
- Pair count: **16**
- Private task-suite SHA-256: `904cb39ea0a06a276c2ee351618f3cf30ec6a83b41cdb13b0ac757a351c961f2`
- Private answer-key SHA-256: `cdf0879ab3fb166ef4d16cd830c2f2fd7d5ef469db1b1dbf1d89376fa9f61258`

The task and key contents are stored only in the external control-plane directory on Sampath's machine and are not committed to candidate-readable GitHub state.

## Independent pre-inference audit

A validator separate from the task generator reproduced **16/16** answer keys before any model inference.

The audit independently checked:
- exhaustive unique minima for both weighted shortest-path tasks;
- exhaustive prerequisite-chain maxima for both critical-path tasks;
- brute-force CRT solutions over a full modulus-product interval;
- exact decimal transaction/reconciliation arithmetic;
- exhaustive permutation uniqueness for ordering tasks;
- direct execution of the exact Python source embedded in code-trace prompts;
- exhaustive bitmask search and unique global optima for constrained subset tasks;
- exhaustive person/topic assignment uniqueness for the logic-grid task.

During pre-inference validation, ambiguous candidate instances were rejected and corrected before the final hashes above were frozen. No model saw any rejected or final v3 task before this preregistration.

## Hard resource envelope

Each Raw and Seed arm receives the same declared maximum envelope:

- max steps: `8`
- max model calls: `12`
- max tool calls: `8`
- max total tokens: `8000`
- max model/API cost: `USD 0`
- Raw per-call output cap: `768`
- Seed planner per-call output cap: `768`
- Seed critic per-call output cap: `128`

Raw uses one direct model call and no tools. Seed may distribute the same hard total token/model-call envelope across its planner/tool/critic loop. Tool execution is measured separately by the existing Gate-1 usage accounting.

## Frozen promotion criteria

The campaign promotes Gate 1 only if all of the following are true:

1. at least **16 valid paired tasks** are sealed;
2. Seed mean accuracy gain over Raw is at least **5 percentage points**;
3. Seed strict paired win rate is at least **60%**;
4. the **95% paired-bootstrap confidence interval** for capability gain has lower bound **> 0**;
5. there is no model/provider/implementation/task-key identity mismatch;
6. no arm exceeds the frozen resource envelope;
7. no evaluator-integrity or fail-closed violation invalidates the evidence.

These thresholds are unchanged from holdout v2. They must not be weakened after observing v3 results.

## Scoring and reporting rule

- The complete 16-pair run must finish under the frozen implementation before architecture changes are considered.
- The sealed evidence is scored against the external key after the run.
- The result must be published whether it passes or fails.
- A failure converts v3 into development evidence; it does not authorize post-hoc threshold changes or reuse as fresh certification data.
- A pass completes Gate 1 and permits Gate-2 empirical promotion work to become the active next gate.

## Claim boundary

Even a Gate-1 pass would show that this bounded Seed scaffold reliably improves a fixed local model under this protocol. It would not, by itself, demonstrate recursive amplification, AGI, or ASI.