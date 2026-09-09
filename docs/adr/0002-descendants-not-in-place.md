# ADR-0002: Self-modification creates descendants, never in-place replacement

**Status:** Accepted

## Context
In-place self-rewriting destroys easy rollback and complicates provenance.

## Decision
Every patch is applied to a copy-on-write descendant workspace. Parent source remains unchanged. Promotion is a separate decision after testing and evaluation.

## Consequences
- clean lineage and rollback;
- higher storage/evaluation overhead;
- simpler audits and A/B comparison.
