# Gate 1 Qualification: Bounded Raw-vs-Seed Agent Infrastructure

Date: 2026-09-09

## Gate-1 question

Gate 1 asks whether the Project Seed scaffold can make a fixed underlying model more capable on long-horizon/tool-using tasks under a controlled external resource envelope.

The scientific comparison is:

```text
same model + same task family + same maximum budget

RAW ARM                         SEED ARM
model -> final answer           model -> planner -> tools -> observations
                                      -> critic -> replan -> final answer
```

The comparison must not quietly substitute a stronger model for the Seed arm or give the Seed arm an unbounded wallet.

## Infrastructure qualification implemented here

`seed gate1-certify` is a deterministic fail-closed canary that validates the machinery required before a frontier-model campaign.

It checks:

1. raw and Seed arms declare the same provider identity;
2. raw and Seed arms receive exactly the same resource envelope;
3. both arms stay inside the declared envelope;
4. the Seed loop can complete a multi-step tool-using task;
5. the comparison harness detects a deliberately planted capability difference;
6. non-allowlisted tool requests are rejected;
7. malformed model JSON fails closed;
8. runaway model calls are blocked by a hard budget;
9. budget exhaustion becomes an explicit terminal state rather than a crash;
10. model-call transcript metadata is recorded and content-hashed.

The canary intentionally uses `ScriptedProvider`. It proves that the **Gate-1 experimental apparatus behaves correctly**. It is not evidence that a frontier GPT model is improved by Seed.

## Hard resource envelope

Gate 1 meters:

- agent steps;
- model calls;
- tool calls;
- total reported tokens;
- reported API/model cost.

`BudgetedProvider` wraps the model interface and records request/response hashes plus reported usage. The raw-model arm and Seed arm are compared with identical maximum limits.

## Failure semantics

The bounded agent converts failures into explicit states:

- `budget_exhausted` for resource-limit violations;
- `blocked` for denied actions such as non-allowlisted tools;
- `failed` for malformed/unhandled provider or component errors.

A failed planner/critic response therefore cannot silently become a successful answer.

## What remains for scientific Gate-1 certification

A real-model campaign must still be run. It should use the same model/version for both arms and private Gate-0 evaluation suites.

Required evidence:

- multiple task families, including long-horizon tasks;
- repeated stochastic trials;
- hidden/OOD scoring through Gate 0;
- equal declared resource envelopes;
- externally recorded model identity/version;
- capability delta and confidence interval;
- normalized efficiency/cost analysis;
- no task/evaluator leakage;
- raw transcripts and Seed transcripts retained as auditable artifacts.

Because normal ChatGPT chat is not an arbitrary programmatic model API, the repository deliberately does not pretend that the deterministic qualification is the frontier campaign. A ChatGPT-backed campaign can be performed through a controlled manual/Work integration or a model API when explicitly available.

## Storage policy during current development

The canonical state is GitHub: `sampathkumar-co/asi`.

While Sampath's laptop is offline, Yaswanth's machine may be used only for stateless validation commands. Gate-1 source, artifacts, test data, and working copies are not to be stored there.
