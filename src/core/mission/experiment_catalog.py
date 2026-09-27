"""Leitura de manifestos reproduziveis de falhas experimentais."""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExperimentDefinition:
    identifier: str
    world_id: str
    recovery: str
    faults: tuple[dict, ...]


def load_experiment(project_directory: Path, identifier: str) -> ExperimentDefinition:
    path = project_directory / "experiments" / "faults" / f"{identifier}.json"
    with path.open(encoding="utf-8") as source:
        data = json.load(source)
    if data.get("id") != identifier or not data.get("world"):
        raise ValueError(f"Manifesto invalido: {path}")
    return ExperimentDefinition(identifier, data["world"], data.get("recovery", "baseline"), tuple(data.get("faults", ())))
