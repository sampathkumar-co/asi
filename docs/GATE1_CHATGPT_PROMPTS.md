# Gate 1 ChatGPT Prompt Templates

These templates are frozen for the Gate-1 ChatGPT pilot. They are intentionally different only in orchestration instructions; task text, model, surface, and declared resource envelope must remain the same.

## Raw arm opening message

```text
You are participating in Project Seed Gate 1 evaluation.

Solve the task below directly using your normal reasoning. Do not use the Project Seed planner/executor/critic protocol. Do not ask the other arm for information. Use only tools explicitly allowed by the task. Stay within the declared resource envelope. Return one final answer clearly marked with FINAL:.

TASK_ID: <task-id>
RESOURCE_ENVELOPE: max_steps=8, max_model_calls=12, max_tool_calls=8, max_tokens=8000, max_cost_usd=0
TASK:
<task text>
```

## Seed arm opening message

```text
You are participating in Project Seed Gate 1 evaluation using the Seed scaffold.

Use this bounded loop:
1. PLAN: identify the next smallest useful subgoal.
2. ACT: perform one permitted action or reasoning step.
3. OBSERVE: record the result/evidence.
4. CRITIQUE: decide whether the evidence is sufficient, whether an error/confound exists, and whether to finish or replan.
5. REPEAT only while useful and inside the declared resource envelope.

Do not use information from the raw arm. Use only tools explicitly allowed by the task. Keep the same underlying model and ChatGPT mode for the entire run. When the success criterion is satisfied, return one final answer clearly marked with FINAL:.

TASK_ID: <task-id>
RESOURCE_ENVELOPE: max_steps=8, max_model_calls=12, max_tool_calls=8, max_tokens=8000, max_cost_usd=0
TASK:
<task text>
```

## Fairness rules

- Start each arm in a fresh conversation.
- Use the exact same task text in both arms.
- Use the same visible ChatGPT model and mode.
- Do not reveal hidden answers or scoring criteria to either arm.
- Do not copy any reasoning or answer from one arm into the other.
- Freeze both outputs before Gate-0 scoring.
- Preserve the transcript as evidence and hash it before analysis.

## Interpretation

A win by the Seed arm on one task is not Gate-1 certification. The campaign requires multiple paired tasks, hidden/OOD Gate-0 scoring, paired confidence analysis, and evidence strong enough to support the declared model/usage metadata.
