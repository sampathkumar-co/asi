# Gate 1 ChatGPT Pilot Tasks v1

These task texts are frozen for the real-chat Gate-1 pilot. Each task must be run twice in separate fresh ChatGPT conversations: once with the Raw opening template and once with the Seed opening template from `docs/GATE1_CHATGPT_PROMPTS.md`.

The answer key is deliberately not stored in the candidate-readable repository. Outputs are frozen before scoring.

## Completed pairs

- T1 — ordering puzzle — Raw and Seed completed.
- T2 — critical-path scheduling — Raw and Seed completed.

## T3 — weighted directed shortest path

Find the unique shortest directed path from S to T. Edges with weights: S->A 4, S->B 7, S->C 3, A->D 5, A->E 9, B->A 2, B->E 3, B->F 8, C->B 2, C->D 6, D->E 1, D->T 8, E->F 2, E->T 5, F->T 2.

Return exactly: `FINAL: <cost> | <path-with-hyphens>`.

## T4 — ledger aggregation

A ledger contains the following records. Only records with status POSTED count. For a sale, net amount is `quantity * unit_price * (1 - discount_percent/100)`. A refund subtracts its listed amount. A fee subtracts its listed amount.

1. Account A: sale, quantity 3, unit price 40.00, discount 10%, POSTED
2. Account B: sale, quantity 2, unit price 55.00, discount 0%, POSTED
3. Account A: refund 25.00, POSTED
4. Account C: sale, quantity 4, unit price 30.00, discount 25%, PENDING
5. Account B: fee 6.50, POSTED
6. Account C: sale, quantity 5, unit price 18.00, discount 20%, POSTED
7. Account A: refund 12.50, VOID
8. Account C: sale, quantity 1, unit price 99.50, discount 0%, POSTED
9. Account C: fee 4.00, POSTED
10. Account B: sale, quantity 2, unit price 75.00, discount 10%, POSTED

Return exactly: `FINAL: A=<2dp>,B=<2dp>,C=<2dp>,TOTAL=<2dp>`.

## T5 — Python aliasing/code trace

Without executing code, determine the exact final printed values:

```python
def f(xs):
    out = []
    for i, x in enumerate(xs):
        if i % 2 == 0:
            xs[i] = x + i
        else:
            out.append(xs[i-1] - x)
    return xs, out

a = [3, 1, 4, 1, 5, 9]
b = a
r = f(a)
b[0] += 2
print(a, r[1], sum(b))
```

Return exactly: `FINAL: <list-a> | <list-r1> | <sum>`.

## T6 — logic-grid deduction

Four researchers — Alex, Bea, Chen, Dev — present once each on Monday through Thursday, and each presents a different topic: AI, Databases, Networks, Operating Systems.

Clues:
- Chen presents on Thursday.
- The Databases presentation is on Monday.
- Alex presents later than Dev.
- The AI presentation is immediately before Alex's presentation.
- Bea presents neither AI nor Operating Systems.
- Dev does not present Networks.

Determine the unique day order and the topic order by day.

Return exactly: `FINAL: <Mon-person>-<Tue-person>-<Wed-person>-<Thu-person> | <Mon-topic>-<Tue-topic>-<Wed-topic>-<Thu-topic>` using topic names `DB`, `AI`, `OS`, `Networks`.

## T7 — modular arithmetic

Find the smallest positive integer n satisfying all three congruences:
- n ≡ 2 (mod 5)
- n ≡ 3 (mod 7)
- n ≡ 4 (mod 9)

Return exactly: `FINAL: <n>`.

## T8 — constrained optimization

Choose a subset of items with total weight at most 15 that maximizes total value.

Items are `(weight,value)`:
- A=(4,9)
- B=(5,11)
- C=(3,7)
- D=(6,14)
- E=(2,5)
- F=(4,10)
- G=(3,8)
- H=(5,13)

Constraints:
- If H is chosen, E must also be chosen.
- D and B cannot both be chosen.
- If F is chosen, C must also be chosen.
- A and G cannot both be chosen.

Return the maximum value and the chosen item letters in alphabetical order.

Return exactly: `FINAL: <value> | <letters-with-hyphens>`.

## Pair execution rule

For every T3–T8 task:

1. Raw and Seed must start in separate fresh conversations.
2. Both must use the same visible model and High reasoning mode.
3. Task text and resource envelope must be byte-for-byte equivalent in substance.
4. Neither arm may receive the other arm's answer or reasoning.
5. Freeze both outputs before scoring.
6. Any UI/clipboard ambiguity invalidates that run and requires a fresh rerun; it must not be counted.
