# Architecture

## Design goals

Project Seed optimizes for experimental clarity before maximal autonomy.

### Invariants

1. The parent running process is not rewritten in place.
2. Candidate-modifiable code cannot modify the canonical evaluator or mutation policy.
3. Every promoted descendant has provenance linking it to a parent and evaluation evidence.
4. Resource budgets are explicit inputs, not informal expectations.
5. Model providers are replaceable; the experiment must not be inseparable from one vendor.
6. Hidden evaluation data must remain outside candidate-readable workspaces.

## Modules

### `seed.core`
Canonical state, budgets and tamper-evident event history.

### `seed.providers`
Provider-neutral model protocol. The repository currently includes only a deterministic scripted provider so tests require no credentials.

### `seed.tools`
Explicit tool registry. Unregistered tools are denied by default.

### `seed.agent`
Gate-1 planner/executor/critic loop.

### `seed.eval`
Gate-0 suites, metrics and receipts. This module is excluded from Gate-4 mutation.

### `seed.science`
Gate-2 hypothesis/experiment/verification structures.

### `seed.search`
Gate-3 declarative architecture genome and bounded evolutionary search.

### `seed.selfmod`
Gate-4 mutation policy, descendant workspaces, sandbox interface and promotion decision. This module is excluded from candidate mutation.

## Event provenance

Each run can write events to SQLite. Events form a SHA-256 chain:

`GENESIS -> H(event_1) -> H(event_2) -> ...`

This detects accidental or post-hoc alteration of stored events. It is not a substitute for externally signed receipts; external signing can be added later.

## Evaluation isolation

Visible smoke tests live in the repository. Real hidden tests must not. Production experiments should mount or inject private evaluation cases into a trusted evaluator process that returns only results/receipts to the candidate process.

## Candidate lifecycle

A source-modifying candidate provides complete replacement content plus the expected hash of the parent file. This prevents silently applying a proposal to a changed parent. The builder copies the repository to an ephemeral workspace and changes only the descendant copy.

## Why Docker is not called a perfect sandbox

The Docker runner reduces privilege but is not a formal isolation boundary against every kernel/container escape. High-stakes experiments should eventually use stronger isolation such as dedicated VMs/microVMs, restricted service accounts, outbound proxies, artifact signing and host-level monitoring.
