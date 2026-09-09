# ADR-0003: Foundation is model-provider neutral

**Status:** Accepted

## Context
The recursive-amplification hypothesis should not depend on one API or model family.

## Decision
Core code depends on a small `ModelProvider` protocol. Deterministic tests use `ScriptedProvider`; real adapters are separate integrations.

## Consequences
- reproducible credential-free unit tests;
- easier cross-model experiments;
- provider-specific features must be expressed through adapters/brokers rather than leaking into core logic.
