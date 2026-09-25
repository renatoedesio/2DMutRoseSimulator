"""Catálogo baseado em pastas para pacotes de missão autocontidos."""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MissionBundle:
    family: str
    scenario_name: str
    domain: str
    simulator_scenario: str
    decomposition_path: Path
    world_db_path: Path


class MissionCatalog:
    """Encontra pacotes de missão em missions/<família>/<cenário>."""

    def __init__(self, missions_directory: Path) -> None:
        self.missions_directory = missions_directory

    def load(self, family: str, scenario_name: str) -> MissionBundle:
        bundle_directory = self.missions_directory / family / scenario_name
        manifest_path = bundle_directory / "manifest.json"
        if not manifest_path.exists():
            raise FileNotFoundError(f"Cenário não encontrado: {family}/{scenario_name}")
        with manifest_path.open(encoding="utf-8") as source:
            manifest = json.load(source)
        return MissionBundle(
            family=family,
            scenario_name=scenario_name,
            domain=manifest["domain"],
            simulator_scenario=manifest["simulator_scenario"],
            decomposition_path=self._bundle_file(bundle_directory, manifest["decomposition"]),
            world_db_path=self._bundle_file(bundle_directory, manifest["world_db"]),
        )

    def list(self) -> list[MissionBundle]:
        if not self.missions_directory.exists():
            return []
        bundles = []
        for family_directory in self.missions_directory.iterdir():
            if not family_directory.is_dir():
                continue
            for scenario_directory in family_directory.iterdir():
                if scenario_directory.is_dir() and (scenario_directory / "manifest.json").exists():
                    bundles.append(self.load(family_directory.name, scenario_directory.name))
        return sorted(bundles, key=lambda item: (item.family, item.scenario_name))

    @staticmethod
    def _bundle_file(bundle_directory: Path, file_name: str) -> Path:
        path = (bundle_directory / file_name).resolve()
        if bundle_directory.resolve() not in path.parents or not path.exists():
            raise FileNotFoundError(f"Arquivo inválido ou ausente no pacote: {file_name}")
        return path
