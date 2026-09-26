"""Seleção de mundos e execução do MutROSe para Room Preparation."""

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MutroseGeneration:
    """Artefatos produzidos para um estado inicial do mundo."""

    world_id: str
    world_db_path: Path
    task_output_path: Path


class MutroseRunner:
    """Materializa um mundo catalogado e pede sua decomposição ao MutROSe."""

    def __init__(self, project_directory: Path) -> None:
        self.project_directory = project_directory
        self.mutrose_directory = project_directory / "mutrose"
        self.room_preparation_directory = self.mutrose_directory / "RoomPreparation"
        self.worlds_directory = self.room_preparation_directory / "Worlds"

    def list_worlds(self) -> list[tuple[str, str]]:
        catalog = self._load_catalog()
        return [(item["id"], item["description"]) for item in catalog["scenarios"]]

    def generate(self, world_id: str) -> MutroseGeneration:
        scenario = next(
            (item for item in self._load_catalog()["scenarios"] if item["id"] == world_id), None
        )
        if scenario is None:
            available = ", ".join(known_id for known_id, _ in self.list_worlds())
            raise ValueError(f"Mundo desconhecido: {world_id}. Disponíveis: {available}")

        source_world = self._world_file(scenario["world_db"])
        active_world = self.worlds_directory / "active" / "World_db.xml"
        active_world.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_world, active_world)

        command = [
            str(self.mutrose_directory / "mutrose.exe"),
            "RoomPreparation/room_preparation.hddl",
            "RoomPreparation/gm_room_preparation.txt",
            "RoomPreparation/configuration.json",
        ]
        process = subprocess.run(command, cwd=self.mutrose_directory, text=True, capture_output=True)
        if process.returncode != 0:
            details = "\n".join(part for part in (process.stdout, process.stderr) if part.strip())
            raise RuntimeError(f"MutROSe terminou com código {process.returncode}.\n{details}")

        generated_output = self.room_preparation_directory / "output" / "task_output.json"
        if not generated_output.exists():
            raise RuntimeError("MutROSe não gerou RoomPreparation/output/task_output.json.")

        archived_output = self.room_preparation_directory / "output" / "runs" / world_id / "task_output.json"
        archived_output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(generated_output, archived_output)
        return MutroseGeneration(world_id, active_world, archived_output)

    def _load_catalog(self) -> dict:
        catalog_path = self.worlds_directory / "catalog.json"
        with catalog_path.open(encoding="utf-8") as source:
            catalog = json.load(source)
        if not isinstance(catalog.get("scenarios"), list):
            raise ValueError("Catálogo de mundos sem lista 'scenarios'.")
        return catalog

    def _world_file(self, relative_path: str) -> Path:
        path = (self.worlds_directory / relative_path).resolve()
        if self.worlds_directory.resolve() not in path.parents or not path.is_file():
            raise FileNotFoundError(f"World DB inválido ou ausente no catálogo: {relative_path}")
        return path
