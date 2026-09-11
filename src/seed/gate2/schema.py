from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class CatalogItem:
    id: str
    text: str

    def public_dict(self) -> dict[str, str]:
        return {"id": self.id, "text": self.text}


@dataclass(frozen=True)
class ResearchExperiment:
    id: str
    description: str
    possible_outcomes: tuple[CatalogItem, ...]
    observed_outcome_id: str
    observation: str

    def public_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "description": self.description,
            "possible_outcomes": [x.public_dict() for x in self.possible_outcomes],
        }

    def reveal(self) -> dict[str, str]:
        return {
            "experiment_id": self.id,
            "outcome_id": self.observed_outcome_id,
            "observation": self.observation,
        }


@dataclass(frozen=True)
class ResearchTask:
    task_id: str
    question: str
    hypotheses: tuple[CatalogItem, ...]
    experiments: tuple[ResearchExperiment, ...]
    controls: tuple[CatalogItem, ...]
    risks: tuple[CatalogItem, ...]
    max_experiments: int = 2

    def public_dict(self) -> dict[str, object]:
        return {
            "task_id": self.task_id,
            "question": self.question,
            "hypotheses": [x.public_dict() for x in self.hypotheses],
            "experiments": [x.public_dict() for x in self.experiments],
            "controls": [x.public_dict() for x in self.controls],
            "risks": [x.public_dict() for x in self.risks],
            "max_experiments": self.max_experiments,
        }

    def experiment(self, experiment_id: str) -> ResearchExperiment:
        for item in self.experiments:
            if item.id == experiment_id:
                return item
        raise KeyError(experiment_id)

    def validate(self) -> None:
        def unique(values: tuple[CatalogItem, ...], label: str) -> None:
            ids = [x.id for x in values]
            if not ids or len(ids) != len(set(ids)):
                raise ValueError(f"{label} ids must be unique and non-empty")

        unique(self.hypotheses, "hypothesis")
        unique(self.controls, "control")
        unique(self.risks, "risk")
        experiment_ids = [x.id for x in self.experiments]
        if not experiment_ids or len(experiment_ids) != len(set(experiment_ids)):
            raise ValueError("experiment ids must be unique and non-empty")
        if not 1 <= self.max_experiments <= min(3, len(self.experiments)):
            raise ValueError("max_experiments must be between 1 and 3")
        for experiment in self.experiments:
            outcome_ids = [x.id for x in experiment.possible_outcomes]
            if not outcome_ids or len(outcome_ids) != len(set(outcome_ids)):
                raise ValueError(f"outcomes for {experiment.id} must be unique and non-empty")
            outcome_texts = [x.text.strip().casefold() for x in experiment.possible_outcomes]
            if any(not text for text in outcome_texts) or len(outcome_texts) != len(set(outcome_texts)):
                raise ValueError(f"outcome descriptions for {experiment.id} must be distinct and non-empty")
            if experiment.observed_outcome_id not in outcome_ids:
                raise ValueError(f"observed outcome for {experiment.id} is not declared")


def _catalog(values: list[dict]) -> tuple[CatalogItem, ...]:
    return tuple(CatalogItem(str(x["id"]), str(x["text"])) for x in values)


def load_research_tasks(path: str | Path) -> tuple[str, tuple[ResearchTask, ...]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    suite_id = str(data["suite_id"])
    tasks: list[ResearchTask] = []
    for raw in data["tasks"]:
        experiments = []
        for item in raw["experiments"]:
            observed = item["observed"]
            experiments.append(ResearchExperiment(
                str(item["id"]),
                str(item["description"]),
                _catalog(item["possible_outcomes"]),
                str(observed["outcome_id"]),
                str(observed["observation"]),
            ))
        task = ResearchTask(
            str(raw["task_id"]), str(raw["question"]), _catalog(raw["hypotheses"]),
            tuple(experiments), _catalog(raw.get("controls", [])), _catalog(raw.get("risks", [])),
            int(raw.get("max_experiments", 2)),
        )
        task.validate()
        tasks.append(task)
    task_ids = [x.task_id for x in tasks]
    if not task_ids or len(task_ids) != len(set(task_ids)):
        raise ValueError("research task ids must be unique and non-empty")
    return suite_id, tuple(tasks)
