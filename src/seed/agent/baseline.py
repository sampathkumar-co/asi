from __future__ import annotations

from seed.core.budget import Budget
from seed.core.events import EventStore
from seed.core.models import AgentState, Goal, RunStatus
from .interfaces import Critic, Executor, Planner


class BaselineAgent:
    """Gate-1 observe/act/critic loop with explicit budgets and event logging."""

    def __init__(self, planner: Planner, executor: Executor, critic: Critic, *, budget: Budget | None = None, events: EventStore | None = None) -> None:
        self.planner = planner
        self.executor = executor
        self.critic = critic
        self.budget = budget or Budget()
        self.events = events

    def _event(self, state: AgentState, kind: str, payload: dict) -> None:
        if self.events:
            self.events.append(state.run_id, kind, payload)

    def run(self, goal: Goal) -> AgentState:
        state = AgentState(goal=goal)
        self._event(state, "run_started", {"goal": goal.description})

        while self.budget.can_step():
            self.budget.charge_step()
            state.step += 1

            task = self.planner.next_task(state)
            state.tasks.append(task)
            self._event(state, "task_planned", {"task_id": task.id, "description": task.description, "tool": task.tool_name})

            self.budget.charge_tool()
            obs = self.executor.execute(task)
            state.observations.append(obs)
            self._event(state, "task_observed", {"task_id": task.id, "ok": obs.ok, "output": obs.output, "error": obs.error})

            critique = self.critic.review(state)
            state.confidence = critique.confidence
            state.notes.append(critique.reason)
            self._event(state, "critic_review", {"done": critique.done, "confidence": critique.confidence, "reason": critique.reason})

            if critique.done:
                state.status = RunStatus.SUCCEEDED
                state.final_answer = critique.final_answer
                self._event(state, "run_completed", {"answer": state.final_answer})
                return state

        state.status = RunStatus.BUDGET_EXHAUSTED
        self._event(state, "run_stopped", {"reason": "budget_exhausted"})
        return state
