import json
import tempfile
import unittest
from pathlib import Path

from seed.gate2.schema import CatalogItem, ResearchExperiment, ResearchTask, load_research_tasks


class Gate2SchemaTests(unittest.TestCase):
    def task(self):
        return ResearchTask(
            "R1",
            "question",
            (CatalogItem("H1", "one"), CatalogItem("H2", "two")),
            (ResearchExperiment(
                "E1", "experiment",
                (CatalogItem("O1", "one"), CatalogItem("O2", "two")),
                "O2", "PRIVATE OBSERVATION",
            ),),
            (CatalogItem("C1", "control"),),
            (CatalogItem("K1", "risk"),),
            1,
        )

    def test_public_dict_hides_observed_outcome(self):
        public = self.task().public_dict()
        encoded = json.dumps(public)
        self.assertNotIn("PRIVATE OBSERVATION", encoded)
        self.assertNotIn("observed_outcome_id", encoded)

    def test_reveal_returns_private_observation(self):
        reveal = self.task().experiment("E1").reveal()
        self.assertEqual(reveal["outcome_id"], "O2")
        self.assertEqual(reveal["observation"], "PRIVATE OBSERVATION")

    def test_duplicate_hypothesis_is_rejected(self):
        task = self.task()
        bad = ResearchTask(
            task.task_id, task.question,
            (CatalogItem("H1", "one"), CatalogItem("H1", "duplicate")),
            task.experiments, task.controls, task.risks, task.max_experiments,
        )
        with self.assertRaises(ValueError):
            bad.validate()

    def test_undeclared_observed_outcome_is_rejected(self):
        task = self.task()
        bad_exp = ResearchExperiment(
            "E1", "experiment", (CatalogItem("O1", "one"),), "OX", "private"
        )
        bad = ResearchTask(
            task.task_id, task.question, task.hypotheses,
            (bad_exp,), task.controls, task.risks, 1,
        )
        with self.assertRaises(ValueError):
            bad.validate()

    def test_duplicate_outcome_descriptions_are_rejected(self):
        task = self.task()
        bad_exp = ResearchExperiment(
            "E1", "experiment",
            (CatalogItem("O1", "same meaning"), CatalogItem("O2", " Same Meaning ")),
            "O1", "private",
        )
        bad = ResearchTask(task.task_id, task.question, task.hypotheses, (bad_exp,), task.controls, task.risks, 1)
        with self.assertRaises(ValueError):
            bad.validate()

    def test_max_experiments_is_bounded(self):
        task = self.task()
        bad = ResearchTask(
            task.task_id, task.question, task.hypotheses,
            task.experiments, task.controls, task.risks, 2,
        )
        with self.assertRaises(ValueError):
            bad.validate()

    def test_loader_rejects_duplicate_task_ids(self):
        task = {
            "task_id": "R1", "question": "q",
            "hypotheses": [{"id": "H1", "text": "h"}],
            "experiments": [{
                "id": "E1", "description": "e",
                "possible_outcomes": [{"id": "O1", "text": "o"}],
                "observed": {"outcome_id": "O1", "observation": "private"},
            }],
            "controls": [{"id": "C1", "text": "c"}],
            "risks": [{"id": "K1", "text": "r"}],
            "max_experiments": 1,
        }
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "tasks.json"
            path.write_text(json.dumps({"suite_id": "s", "tasks": [task, task]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_research_tasks(path)


if __name__ == "__main__":
    unittest.main()
