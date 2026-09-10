# Gate 1 Local Holdout V2 — Preregistration

Status: frozen before first model inference on this holdout.

## Candidate

- Seed source commit frozen for evaluation: `8c18f91ad72c31007243e4bf2b8388b1421efd00`
- Local model: `qwen3:8b`
- Ollama model digest: `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`
- Model size: 5,225,388,164 bytes
- Temperature: 0
- Thinking: off
- Context: 4096 tokens

## Private holdout identity

The task suite and answer key remain outside the candidate-readable repository.

- Suite ID: `gate1-local-holdout-v2`
- Number of paired tasks: 16
- Task file SHA-256: `e44d93fcc949d4d43750b3feca3175039e65019c43e21140aaeb758625763411`
- External answer-key SHA-256: `b86ed624705a7b68bcc1136cf77fd30058f7537969a1f24e42647b30b3b55b18`

An independent pre-run audit reproduced all 16 expected answers. Tasks requiring uniqueness were exhaustively checked: shortest paths, critical paths, assignment/order puzzles, and constrained-optimization maxima each have exactly one optimum/solution.

## Resource envelope

Raw and Seed use the same underlying model and hard arm-level envelope:

- max steps: 8
- max model calls: 12
- max tool calls: 8
- max total tokens: 8000
- max cost: USD 0
- raw per-call output cap: 768
- Seed planner per-call output cap: 768
- Seed critic per-call output cap: 128

Raw receives one bounded analysis+answer model call and no tools. Seed uses the frozen planner/tool/critic architecture with deterministic capability routing and verified tool evidence.

## Promotion rule

The promotion rule is fixed before evaluation and is not changed after seeing holdout results:

1. all 16 paired tasks must have valid same-model/same-envelope evidence;
2. Seed mean accuracy gain over Raw must be at least 0.05;
3. Seed strict paired win rate must be at least 0.60;
4. the 95% paired-bootstrap confidence interval for Seed-minus-Raw accuracy gain must have lower bound strictly greater than 0;
5. no budget or integrity violation may occur.

Bootstrap sampling uses 4,000 paired resamples, matching the existing Gate 1 campaign methodology.

This holdout is independent of the earlier T1–T8 development/calibration suite. No architecture changes are permitted after the first holdout inference if the run is to count as this preregistered evaluation.