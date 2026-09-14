# Gates 0-4

A gate has two levels of evidence:

1. **Infrastructure qualification** — the machinery behaves correctly under deterministic canaries.
2. **Empirical certification** — real model/research runs satisfy the preregistered scientific criterion on hidden/OOD evaluations.

## Gate 0 — Evaluation infrastructure

### Objective
Establish trustworthy measurement before optimization begins.

### Status
**COMPLETE / infrastructure-qualified.**

The fail-closed `seed gate0-certify` command validates external holdout separation, known-good/known-bad discrimination, statistical comparison, receipt integrity, tamper rejection and evaluator immutability.

### Scientific role
Gate 0 is the measurement instrument used to judge every later capability claim.

---

## Gate 1 — Bounded baseline agent

### Objective
Determine whether a scaffold improves a fixed model under a controlled resource envelope.

### Status
**COMPLETE / EMPIRICALLY CERTIFIED.**

The preregistered 16-pair local Qwen3-8B holdout v5 completed on 2026-09-10. Raw scored **1/16 = 6.25%** and Seed scored **15/16 = 93.75%**, a **+87.50 pp** mean gain. Strict Seed win rate was **14/16 = 87.50%** and the 95% paired-bootstrap CI was **[+68.75 pp, +100.00 pp]**. Identity/integrity and resource-envelope audits passed, so every frozen promotion criterion passed.

Frozen v5 source: `c34e1cd31c61efebc513f289ba9ac11cdd4412d0`; implementation digest: `011881547d85a31cccc3bd66a174e7ae9b3e8506014a6c918d248e78708e286c`; preregistration: `857aa0f4cac7437deb86646e6f72d682b16d806a`.

See [`GATE1_LOCAL_HOLDOUT_V5_RESULT.md`](GATE1_LOCAL_HOLDOUT_V5_RESULT.md). Earlier failed holdouts remain published as retired historical evidence.

### Implemented
- raw-model control arm;
- planner/executor/critic Seed arm;
- persistent state/provenance;
- hard model/tool/step/token/cost budgets;
- model-call metering and transcript hashes;
- local Ollama adapter and exact model digest attestation;
- explicit relevant-tool routing and allowlists;
- exact reusable graph/scheduling/CRT, semantic transaction/reconciliation, Python-trace, subset-optimization and CSP tools;
- sandboxed computation fallback;
- fail-closed malformed-output and budget behavior;
- same-provider/same-envelope comparison evidence;
- per-pair checkpoint/resume;
- implementation digest attestation;
- external-key scoring and paired bootstrap;
- deterministic `seed gate1-certify` infrastructure canary.

### Infrastructure criterion
The qualification must prove that both arms use the same declared provider identity and envelope, that overspending and denied actions fail closed, and that the harness can detect a planted multi-step capability difference.

### Empirical criterion
Before inference, freeze the candidate implementation, exact model artifact, private task/key hashes, resource envelope and promotion thresholds. Using the same model artifact for both arms, Seed must outperform Raw on a new hidden/OOD campaign while remaining inside the common resource envelope.

The current promotion rule requires:
- at least 16 valid paired tasks;
- mean Seed capability gain >= 5 percentage points;
- strict Seed paired win rate >= 60%;
- 95% paired-bootstrap CI lower bound > 0;
- no integrity or resource-envelope violation.

A failed holdout becomes development evidence. Its tasks cannot be reused as fresh certification data after architecture changes.

---

## Gate 2 — Scientific-method and verification layer

### Objective
Make the system reason in terms of falsifiable hypotheses and independent evidence.

### Status
**V3.1 private-v31 completed; frozen mean-gain criterion failed; NOT empirically certified.**

### Implemented
- one hidden-safe pre-reveal outcome-to-hypothesis causal-attribution call;
- strict complete experiment/outcome/support-set validation;
- runner-fixed **3:1** canonical likelihood conversion with no model probability magnitudes;
- runner-derived information-gain experiment selection;
- controlled reveal followed by Bayesian posterior update;
- runner-derived Bayes-factor rejection and final hypothesis;
- bounded fail-closed schema repair with transcript evidence;
- independent and adversarial support-set verifier calls with >=0.8 audit-confidence requirement;
- trusted verdicts that reject mechanical ties, lower-support finals, or concrete direct evidence defects;
- external-key scoring and deterministic paired bootstrap.

Private v1, v2, and private-v31 are permanently retired as fresh certification evidence. The evaluated v3.1 implementation digest is `c0abee591ed723a46ba57b527c2189efc0d711f3d3a423866a611503e8f16ce8`; deterministic qualification is **46/46 PASS**. Public development scoring is Raw **0.76875**, Seed **0.98750**, gain **+0.21875**, strict wins **75%**, CI **[+0.06250, +0.46875]**, verifier acceptance **100%**. This is not certification evidence.

Frozen source commit `2b98491641426f9ebe1678b8491a18a583e6c784` and preregistration commit `393c22abf67e70675870f7f054eed023685cc08b` were CI-green before inference. Private-v31 completed all 18 pairs: Raw **0.78750**, Seed **0.93472**, mean gain **+0.14722**, strict wins **77.78%**, CI **[+0.01806, +0.28472]**, verifier acceptance **83.33%**. Mean gain failed the frozen **>=0.15** requirement, so `promotion_pass=false`. V31P01 Raw was additionally contaminated by a confirmed Ollama/CUDA startup crash; excluding that pair diagnostically lowers gain to **+0.09706**, so the incident cannot convert the attempt into a pass. The holdout is retired; see [GATE2_PRIVATE_HOLDOUT_V31_RESULT.md](GATE2_PRIVATE_HOLDOUT_V31_RESULT.md).

Post-v31 vNext development adds explicit execution-integrity failure classes. Provider/transport and trusted-runner defects invalidate the campaign through a mandatory `clean_execution` check; model/protocol failures and budget exhaustion continue to fail closed at arm level. Purpose-specific, task-independent JSON Schemas constrain normal Gate-2 Ollama outputs without encoding scientific IDs or answers. A fixed task-independent provider-readiness preflight runs outside the scored envelope before the first unfinished pair and aborts before scored evidence on provider failure. Schema recovery is capped at **two repair calls total per arm**, shared across stages and verifiers; qualification proves maximum three-experiment worst cases of Raw **10** and Seed **16** model calls inside the unchanged 16-call envelope. Current validation is **181/181 tests** and **59/59 deterministic Gate-2 canaries**. The exact-candidate final public-development run remains non-certifying but clean: Raw **0.80000**, Seed **0.98750**, gain **+0.18750**, strict wins **87.5%**, CI **[+0.090625, +0.31875]**, verifier acceptance **100%**, zero repairs, and zero incidents. See [GATE2_VNEXT_FINAL_PUBLIC_RESULT.md](GATE2_VNEXT_FINAL_PUBLIC_RESULT.md).

### Empirical criterion
Any future Gate-2 certification attempt must use a newly created preregistered private/OOD campaign and retain the frozen requirements: >=16 valid pairs, Seed mean >=0.75, mean gain >=0.15, strict Seed wins >=60%, paired-bootstrap lower bound >0, verifier acceptance >=75%, and no identity/integrity/resource/protocol mismatch.

## Gate 3 — Automatic architecture search

### Objective
Search agent architectures instead of assuming a fixed human design.

### Status
**Foundation implemented; not empirically certified.**

### Implemented
- declarative `AgentGenome`;
- bounded mutations;
- archive/deduplication;
- capability-cost fitness;
- multi-generation search.

### Empirical criterion
Discovered architectures must outperform human-written baselines on new hidden/OOD suites under normalized cost.

---

## Gate 4 — Controlled self-modification

### Objective
Allow capability-plane source changes without allowing candidates to rewrite their evaluator/control plane.

### Status
**Control foundation implemented; not empirically certified.**

### Implemented
- structured patches;
- path/byte/file mutation limits;
- evaluator/control/provider denial paths;
- stale-hash protection;
- copy-on-write descendants;
- durable lineage;
- no-network/read-only Docker execution;
- explicit promotion evidence gate.

### Empirical criterion
A child must pass sandbox tests, independent verification and a new hidden/OOD evaluation before human-approved promotion.
