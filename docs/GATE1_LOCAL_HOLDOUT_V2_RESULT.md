# Gate 1 Local Holdout V2 — Result

Date: 2026-09-10

## Verdict

**Gate 1 is not empirically certified by this campaign.**

The preregistered 16-pair Qwen3-8B Raw-vs-Seed holdout showed a real positive capability delta, but it did not satisfy all frozen promotion criteria.

| Metric | Raw | Seed / comparison |
|---|---:|---:|
| Correct | 1/16 | 5/16 |
| Accuracy | 6.25% | 31.25% |
| Mean capability gain | — | **+25 percentage points** |
| Strict Seed win rate | — | **31.25%** |
| 95% paired-bootstrap CI for gain | — | **[0.00, 0.50]** |

Frozen promotion requirements were: at least 16 valid pairs, mean gain >= 5 percentage points, strict Seed win rate >= 60%, CI lower bound > 0, and no integrity/resource violation. Pair count and mean gain passed; win rate and CI did not. Therefore promotion is **FAIL**.

## Preregistered identity

The campaign was preregistered before the first holdout inference in commit `8f38b01604964b1e6aabbef10d842051c52fb25c`.

- Seed source commit: `8c18f91ad72c31007243e4bf2b8388b1421efd00`
- Seed implementation digest: `ab3a568ad1dcf659a1d73e04a5066b30009eb88f57436dcf99e76f92f31459a9`
- model: `qwen3:8b`
- model digest: `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`
- task-suite SHA-256: `e44d93fcc949d4d43750b3feca3175039e65019c43e21140aaeb758625763411`
- answer-key SHA-256: `b86ed624705a7b68bcc1136cf77fd30058f7537969a1f24e42647b30b3b55b18`
- evidence content hash: `30e3fdd748c6c083dff24ed202f71a9ea01c17a3c006fd1e4af478f2b60d70f3`
- evidence file SHA-256: `c502233aabdc741ce5b124a866e100153e08f80883dc90b34ebb767cffa70f9c`

The private tasks, answer key, and raw evidence remain outside candidate-readable source control. The public score-only artifact is [`artifacts/gate1-local-holdout-v2-score.json`](../artifacts/gate1-local-holdout-v2-score.json).

## Resource envelope

Both arms used the same declared hard envelope:

- max steps: 8
- max model calls: 12
- max tool calls: 8
- max total tokens: 8000
- max model cost: USD 0
- temperature: 0
- context: 4096
- Raw/planner per-call output cap: 768
- critic per-call output cap: 128

Raw received one direct model call with bounded scratch analysis and no tools. Seed used the same model behind deterministic goal-based tool routing plus bounded planner/tool/critic orchestration.

## Per-task outcome

| Task | Raw | Seed | Paired outcome |
|---|---:|---:|---|
| H01 | 0 | 1 | Seed win |
| H02 | 0 | 1 | Seed win |
| H03 | 1 | 0 | Raw win |
| H04 | 0 | 0 | tie |
| H05 | 0 | 1 | Seed win |
| H06 | 0 | 1 | Seed win |
| H07 | 0 | 0 | tie |
| H08 | 0 | 0 | tie |
| H09 | 0 | 0 | tie |
| H10 | 0 | 0 | tie |
| H11 | 0 | 0 | tie |
| H12 | 0 | 1 | Seed win |
| H13 | 0 | 0 | tie |
| H14 | 0 | 0 | tie |
| H15 | 0 | 0 | tie |
| H16 | 0 | 0 | tie |

Observed transfer was strongest on the two unseen shortest-path tasks, both CRT tasks, and one constrained-optimization task. Remaining weaknesses include critical-path revision stability, ledger/reconciliation translation, code tracing, some assignment/output-format cases, and budget exhaustion on several hard tasks.

## Scoring incident and correction

The first post-run scoring attempt incorrectly returned all-zero scores because the scorer had two format assumptions not covered by its tests:

1. it treated a single answer-key string as an iterable of characters instead of one accepted answer;
2. it stripped `FINAL:` from model outputs but did not normalize `FINAL:` when it appeared in the external key.

These were evaluator-side parsing bugs. They did **not** change the frozen Seed implementation, model run, private tasks, key, or evidence. The bugs were fixed only after all 16 pairs had completed, with regression tests added. The full repository then passed **121/121 tests** locally on Sampath.

The corrected score has content hash `0f0232399af22525081fa47c49576f1bec9121672a75a7dd628f1e51ebc5c125` and file SHA-256 `46be288c1a9762852e6c0dcd26f6cd65b5984b33b6c9eed9c66e4efb2d0b9946`.

## Interpretation

This campaign is evidence that the current Seed scaffold can improve a fixed small local model on some unseen task classes under the shared hard resource envelope. It is **not** evidence that Gate 1 has passed, that the improvement is statistically robust enough for promotion, or that recursive amplification has been demonstrated.

The next Gate-1 candidate should be improved using this holdout only as development evidence, then frozen and evaluated on a new unseen holdout. Reusing H01-H16 as certification evidence would contaminate the test.

See also:

- [`GATE1_LOCAL_HOLDOUT_V2_PREREGISTRATION.md`](GATE1_LOCAL_HOLDOUT_V2_PREREGISTRATION.md)
- [`GATE1_CERTIFICATION.md`](GATE1_CERTIFICATION.md)
- [`STATUS.md`](STATUS.md)
- [`ROADMAP.md`](ROADMAP.md)
