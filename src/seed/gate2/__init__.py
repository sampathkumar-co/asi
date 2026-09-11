"""Gate-2 empirical scientific-method benchmark infrastructure."""

from .schema import CatalogItem, ResearchExperiment, ResearchTask, load_research_tasks

__all__ = [
    "CatalogItem",
    "ResearchExperiment",
    "ResearchTask",
    "load_research_tasks",
]
