# Gate 1 Real-ChatGPT Campaign Protocol

Date: 2026-09-09

## Purpose

This protocol lets Project Seed use the ChatGPT product itself as the model substrate for Gate 1 without pretending that a normal chat session provides the same machine-verifiable metadata as an API run.

The scientific question remains:

> Does the Seed scaffold improve the same underlying model on the same tasks under the same declared resource envelope?

## Two arms

### Raw arm
A fresh ChatGPT conversation receives the task and solves it directly without the Project Seed planner/executor/critic protocol.

### Seed arm
A separate fresh ChatGPT conversation uses the Project Seed protocol: explicit subgoals, tool actions when permitted, observations, critique, replanning, and a final answer.

Both arms must declare the same:

- provider (`openai-chatgpt` for this campaign);
- model identifier visible in the product;
- ChatGPT surface/mode;
- task identifier;
- maximum resource envelope.

Do not compare different ChatGPT models, different reasoning settings, or different task text and call that a Seed gain.

## Fresh-session rule

Each arm starts in a fresh conversation with no task-specific information from the other arm. Do not paste the raw answer into the Seed arm or vice versa. The benchmark answer/scorer must remain outside both conversations.

## Evidence levels

Project Seed records one of three evidence levels:

1. `manual_chat` — transcript copied from ChatGPT manually. Useful for pilots, but model identity and usage may be only declared/self-reported.
2. `platform_export` — transcript/metadata exported by the platform and retained without editing.
3. `api_attested` — model identity and usage come from a programmatic provider response or equivalent trusted metadata.

A `manual_chat` pair can demonstrate that the workflow runs with real ChatGPT, but by itself cannot produce Project Seed's strongest empirical Gate-1 certification claim.

## Transcript JSON

Each arm is stored as JSON in the evidence system (GitHub artifact or trusted external evidence store, not on Yaswanth's laptop):

```json
{
  "arm": "raw",
  "task_id": "hidden-task-001",
  "provider_id": "openai-chatgpt",
  "model_id": "gpt-5.6-sol",
  "surface_id": "chatgpt-web",
  "evidence_level": "manual_chat",
  "limits": {
    "max_steps": 8,
    "max_model_calls": 12,
    "max_tool_calls": 8,
    "max_tokens": 8000,
    "max_cost_usd": 0.0
  },
  "usage": {
    "steps": 1,
    "model_calls": 1,
    "tool_calls": 0,
    "tokens": 0,
    "cost_usd": 0.0
  },
  "turns": [
    {"role": "user", "content": "<task text>"},
    {"role": "assistant", "content": "<response>"}
  ],
  "final_answer": "<final answer>",
  "gate0_receipt_hash": null,
  "model_identity_attested": false,
  "usage_attested": false
}
```

The Seed arm uses the same schema with `"arm": "seed"`.

## Validation

Run:

```bash
seed gate1-chat-validate --raw raw.json --seed seed.json
```

The validator fails if:

- task IDs differ;
- providers differ;
- model IDs differ;
- ChatGPT surfaces/modes differ;
- resource envelopes differ;
- either arm exceeds the declared envelope;
- transcript structure is invalid;
- a Gate-0 receipt hash is malformed.

It emits hashes for each run and the pair so later transcript edits are visible.

## Hidden evaluation

The task answer and scoring logic must not be present in the chat prompt or candidate-readable repository. After both arms are frozen, the trusted Gate-0 evaluator scores the final answers and issues receipts. Only the receipt hashes need to be attached to the paired evidence.

## Certification rule

For the strongest Gate-1 empirical claim, a pair must have:

- at least `platform_export` evidence level;
- attested model identity for both arms;
- attested usage for both arms;
- valid Gate-0 receipt hashes for both arms;
- equal model/provider/surface/task/resource envelope;
- no overspend.

Manual ChatGPT runs remain valuable pilot evidence and can guide engineering, but Project Seed will label them honestly rather than calling them fully attested certification data.

## Current machine/storage policy

Until Sampath's laptop is online:

- Yaswanth's machine may be used only for stateless interaction/validation;
- do not clone Project Seed or save Gate-1 project/evidence files there;
- canonical source remains `sampathkumar-co/asi`;
- CI/test artifacts remain in GitHub Actions;
- private benchmark answers remain outside candidate-readable GitHub source.
