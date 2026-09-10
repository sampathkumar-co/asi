# Gate 1 Local Holdout v4 Preregistration

Date: 2026-09-10

Status: **FROZEN BEFORE MODEL INFERENCE**

This document preregisters the next Project Seed Gate-1 local promotion attempt. Private task and answer-key contents remain outside source control. Only their hashes, audit result, candidate/model identities, resource envelope and promotion rules are public.

## Frozen candidate

- Seed source commit: `b4242af758b1222f8ecea0bf7306e917a36ed9d8`
- Seed implementation digest: `f9d882e185b235d0a8345640ee1577edb518be96dbf8af0f6b50ec204f5a1358`
- Attested implementation files: 27
- Local validation before preregistration: **134/134 tests PASS**
- Deterministic Gate-1 qualification: **10/10 PASS**
- Qualification content hash: `357b3beac3bbcfb04ccf09b6e00a74dd7fdd95b2ef9ae72f7dd15fc9cff16799`
- GitHub documentation head before preregistration: `e2704a478aaa7dff21e39dd2a6ad26b4e8ebd271`
- GitHub Actions CI #142: **success**

No Seed architecture change is permitted after the first v4 holdout inference if the run is to count toward promotion.
## Frozen model

- Provider: local Ollama
- Model: `qwen3:8b`
- Exact model digest: `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`
- Temperature: `0`
- Context window: `4096`
- Internal thinking mode: disabled

Raw and Seed use the same local model artifact.

## Private holdout identity

- Suite ID: `gate1-local-holdout-v4`
- Pair count: **16**
- Task-suite SHA-256: `a507c95ce85a0adef30f9bf217e49cb3e27824ddc1bd69aedb67d7c32f51b7ad`
- Answer-key SHA-256: `f93e0aaeac12721882c37f2cca2f3f7b8ae28357793214d4c4ea8f4c91c96eac`
- Answer-key container: repository-native `{"suite_id": ..., "answers": {...}}`

A separate validator reproduced **16/16** answer keys before inference, including uniqueness/optimality checks where applicable.
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

Raw uses one direct model call and no tools. Seed may distribute the same hard total envelope across its bounded planner/tool/critic loop.

## Frozen promotion criteria

Gate 1 promotes only if all are true: at least **16 valid pairs**; Seed mean accuracy gain >= **5 percentage points**; strict paired Seed win rate >= **60%**; 95% paired-bootstrap CI lower bound for gain **> 0**; no identity/integrity mismatch; no resource-envelope violation; no fail-closed/evaluator-integrity violation.

These thresholds are unchanged after holdouts v2 and v3. They will not be weakened after observing v4.
