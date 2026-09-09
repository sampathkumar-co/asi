# ADR-0001: Separate capability, evaluation and control planes

**Status:** Accepted

## Context
A self-improving agent that can change its own scoring or promotion logic can create apparent progress without real capability gain.

## Decision
Gate-4 mutations are allowed only under capability-plane paths. Evaluator, self-modification policy, provider credentials and CI remain outside the candidate mutation allowlist.

## Consequences
- fewer degrees of freedom for early self-modification;
- much stronger provenance and falsifiability;
- future expansion requires explicit policy/version changes by maintainers.
