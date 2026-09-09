from __future__ import annotations

from seed.core.models import AgentState, Observation, Task
from seed.tools.registry import ToolRegistry
from .interfaces import Critique


class QueuePlanner:
    """Simple deterministic baseline planner used to establish a measurable floor."""

    def __init__(self, tasks: list[Task]) -> None:
        self.tasks = list(tasks)
        self.index = 0

    def next_task(self, state: AgentState) -> Task:
        if self.index >= len(self.tasks):
            return Task(description="No work remains", tool_name="echo", tool_input={"text": "DONE"})
        task = self.tasks[self.index]
        self.index += 1
        return task


class RegistryExecutor:
    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

    def execute(self, task: Task) -> Observation:
        if not task.tool_name:
            return Observation(task.id, False, error="Task has no tool")
        result = self.registry.call(task.tool_name, task.tool_input)
        return Observation(task.id, result.ok, output=result.output, error=result.error)


class CompletionCritic:
    """Baseline critic: succeeds when N successful observations are present."""

    def __init__(self, required_successes: int) -> None:
        self.required_successes = required_successes

    def review(self, state: AgentState) -> Critique:
        successes = [o for o in state.observations if o.ok]
        if len(successes) >= self.required_successes:
            outputs = [str(o.output) for o in successes[-self.required_successes :]]
            return Critique(True, 1.0, "Required successful observations collected", " | ".join(outputs))
        return Critique(False, len(successes) / max(self.required_successes, 1), "More successful evidence required")
