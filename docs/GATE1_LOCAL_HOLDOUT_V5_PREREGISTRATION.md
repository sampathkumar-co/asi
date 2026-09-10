# Gate 1 Local Holdout v5 Preregistration

Date: 2026-09-10

Status: **FROZEN BEFORE MODEL INFERENCE**

This document preregisters the next Project Seed Gate-1 local promotion attempt. Private task and answer-key contents remain outside source control. Only their hashes, independent audit result, candidate/model identities, resource envelope and promotion rules are public.

## Frozen candidate

- Seed source commit: `c34e1cd31c61efebc513f289ba9ac11cdd4412d0`
- Seed implementation digest: `011881547d85a31cccc3bd66a174e7ae9b3e8506014a6c918d248e78708e286c`
- Attested implementation files: 27
- Local validation before preregistration: **140/140 tests PASS**
- Deterministic Gate-1 qualification: **10/10 PASS**
- Qualification content hash: `357b3beac3bbcfb04ccf09b6e00a74dd7fdd95b2ef9ae72f7dd15fc9cff16799`
- GitHub documentation head before preregistration: `b2b6d7d81303589576c0c8a03ed4e8c8e6d3bd45`
- GitHub Actions CI #145 (source candidate): **success**
- GitHub Actions CI #146 (documentation head): **success**

No Seed architecture change is permitted after the first v5 holdout inference if the run is to count toward promotion.
## Frozen model

- Provider: local Ollama
- Model: `qwen3:8b`
- Exact model digest: `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`
- Temperature: `0`
- Context window: `4096`
- Internal thinking mode: disabled

Raw and Seed use the same local model artifact.

## Private holdout identity

- Suite ID: `gate1-local-holdout-v5`
- Pair count: **16**
- Task-suite SHA-256: `0e51dd6b8dc99e0e68589894b457fe5b80e98ea7815aeeb282cb25df5cf03b5b`
- Answer-key SHA-256: `b86e19c1447f7556ecb2192e01889abdcf8dcc7704d2cd97c8bac1ae34784ad1`
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

These thresholds are unchanged from prior holdouts and will not be weakened after observing v5.