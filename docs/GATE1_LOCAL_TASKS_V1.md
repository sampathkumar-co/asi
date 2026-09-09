# Gate 1 Local-Model Tasks v1

This suite is the first local-model discrimination campaign for Gate 1. It is derived from the ChatGPT pilot, but T6 is corrected because the original T6 clues were underdetermined.

The answer key is deliberately not stored in the candidate-readable repository. Scoring is performed by the trusted evaluation plane after outputs are frozen.

## T1 — ordering puzzle
Seven jobs A,B,C,D,E,F,G must be arranged in positions 1-7. D is immediately after B. A is before F. C is not first or last. G is before A. E is after F. B is before C. Exactly two positions lie between G and C. B is before G. Determine the unique order. Return exactly: `FINAL: <7-letter-order>`.

## T2 — critical-path scheduling
A project has tasks: A duration 4 no prerequisites; B duration 6 no prerequisites; C duration 3 after A; D duration 5 after A; E duration 4 after both B and C; F duration 2 after C; G duration 7 after both D and E; H duration 3 after both F and E; I duration 2 after both G and H. Unlimited parallel workers are available. Find the minimum project completion time and the critical path. Return exactly: `FINAL: <time> | <path-with-hyphens>`.

## T3 — weighted directed shortest path
Find the unique shortest directed path from S to T. Edges with weights: S->A 4, S->B 7, S->C 3, A->D 5, A->E 9, B->A 2, B->E 3, B->F 8, C->B 2, C->D 6, D->E 1, D->T 8, E->F 2, E->T 5, F->T 2. Return exactly: `FINAL: <cost> | <path-with-hyphens>`.

## T4 — ledger aggregation
A ledger contains the following records. Only POSTED records count. A sale contributes `quantity * unit_price * (1-discount_percent/100)`; refunds and fees subtract their amount. Records: A sale 3x40.00 10% POSTED; B sale 2x55.00 0% POSTED; A refund 25.00 POSTED; C sale 4x30.00 25% PENDING; B fee 6.50 POSTED; C sale 5x18.00 20% POSTED; A refund 12.50 VOID; C sale 1x99.50 0% POSTED; C fee 4.00 POSTED; B sale 2x75.00 10% POSTED. Return exactly: `FINAL: A=<2dp>,B=<2dp>,C=<2dp>,TOTAL=<2dp>`.

## T5 — Python aliasing/code trace
Without executing the original program, determine the exact final printed values for: `f(xs)` mutates even indices by adding the index and appends `xs[i-1]-x` at odd indices; `a=[3,1,4,1,5,9]`; `b=a`; `r=f(a)`; `b[0]+=2`; print `a, r[1], sum(b)`. Return exactly: `FINAL: <list-a> | <list-r1> | <sum>`.

## T6 — corrected logic-grid deduction
Four researchers Alex, Bea, Chen, Dev present once each Monday through Thursday, each a different topic AI, Databases, Networks, Operating Systems. Chen presents Thursday. Databases is Monday. Alex presents later than Dev. AI is immediately before Alex's presentation. Bea presents neither AI nor Operating Systems. Dev does not present Networks. **Chen presents Networks.** Determine the unique day order and topic order. Return exactly: `FINAL: <Mon-person>-<Tue-person>-<Wed-person>-<Thu-person> | <Mon-topic>-<Tue-topic>-<Wed-topic>-<Thu-topic>` using `DB`, `AI`, `OS`, `Networks`.

## T7 — modular arithmetic
Find the smallest positive integer n satisfying n ≡ 2 (mod 5), n ≡ 3 (mod 7), n ≡ 4 (mod 9). Return exactly: `FINAL: <n>`.

## T8 — constrained optimization
Choose a subset of items with total weight at most 15 maximizing total value. A=(4,9), B=(5,11), C=(3,7), D=(6,14), E=(2,5), F=(4,10), G=(3,8), H=(5,13). Constraints: if H is chosen, E must also be chosen; D and B cannot both be chosen; if F is chosen, C must also be chosen; A and G cannot both be chosen. Return exactly: `FINAL: <value> | <letters-with-hyphens>`.

## Frozen comparison envelope
- same exact local model and quantization for Raw and Seed;
- temperature 0;
- thinking mode disabled for both arms;
- context 4096;
- maximum 8 Seed steps;
- maximum 12 model calls;
- maximum 8 tool calls;
- maximum 8000 total metered tokens;
- cost USD 0;
- Raw may use its token budget in a single direct call; Seed may allocate the same total budget across bounded calls;
- outputs are frozen before trusted scoring;
- candidate code never receives the answer key.
