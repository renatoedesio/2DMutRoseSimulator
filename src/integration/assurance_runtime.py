"""Adapter local entre o Simulator2D e o pacote Python ``assurance``."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml
from assurance import AssuranceService, EvidenceReport, MissionContract, __version__ as assurance_version


class RunArtifacts:
    """Persiste canais de experimento separados em um diretório de execução."""

    def __init__(self, directory: Path) -> None:
        self.directory = directory

    @classmethod
    def create(
        cls,
        project_directory: Path,
        family: str,
        domain: str,
        scenario_name: str,
        contract_path: Path,
    ) -> "RunArtifacts":
        run_id = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
        directory = project_directory / "runs" / cls._slug(family) / cls._slug(domain) / cls._slug(scenario_name) / run_id
        suffix = 1
        while directory.exists():
            directory = directory.with_name(f"{run_id}_{suffix:02d}")
            suffix += 1
        directory.mkdir(parents=True)
        contract_bytes = contract_path.read_bytes()
        cls._write_json(
            directory / "run_manifest.json",
            {
                "run_id": directory.name,
                "started_at": datetime.now(timezone.utc).isoformat(),
                "assurance_core_version": assurance_version,
                "contract_path": str(contract_path),
                "contract_sha256": hashlib.sha256(contract_bytes).hexdigest(),
            },
        )
        return cls(directory)

    @staticmethod
    def _slug(value: str) -> str:
        return value.replace(" ", "_").replace("-", "_").casefold()

    @staticmethod
    def _write_json(path: Path, payload: dict[str, Any]) -> None:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def append(self, name: str, payload: Any) -> None:
        serialized = asdict(payload) if is_dataclass(payload) else payload
        with (self.directory / name).open("a", encoding="utf-8") as destination:
            destination.write(json.dumps(serialized, ensure_ascii=False) + "\n")


class AssuranceRuntime:
    """Avalia EvidenceReports sem expor o estado verdadeiro ao assurance core."""

    def __init__(self, contract_path: Path, artifacts: RunArtifacts | None = None) -> None:
        with contract_path.open(encoding="utf-8") as source:
            document = yaml.safe_load(source)
        if not isinstance(document, dict):
            raise ValueError(f"Contrato de assurance inválido: {contract_path}")
        self.contract_path = contract_path
        self.contract = MissionContract(document)
        self.service = AssuranceService(self.contract, thresholds={})
        self.artifacts = artifacts
        self._evidence_sequence = 0

    def validate_tasks(self, task_keys: set[str]) -> None:
        missing = sorted(task_keys.difference(self.contract.document.get("tasks", {})))
        if missing:
            raise ValueError(f"Contrato de assurance sem tarefas: {', '.join(missing)}")

    def assess_reachability(
        self,
        task_id: str,
        path_status: str,
        *,
        localization_sigma_m: float,
        measured_position_m: tuple[float, float],
        source: str = "simulator2d_navigation_sensor",
    ) -> tuple[Any, ...]:
        bindings = self.contract.document["tasks"].get(task_id, {}).get("assumptions", [])
        reachability_ids = [item["id"] for item in bindings if item.get("type") == "Reachability"]
        assessments = []
        for assumption_id in reachability_ids:
            self._evidence_sequence += 1
            report = EvidenceReport(
                mission_id=self.contract.mission_id,
                task_id=task_id,
                assumption_id=assumption_id,
                evidence_id=f"evidence-{self._evidence_sequence:04d}",
                payload={
                    "path_status": path_status,
                    "localization_sigma": localization_sigma_m,
                    "measured_position_m": {"x": measured_position_m[0], "y": measured_position_m[1]},
                },
                source=source,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            assessment = self.service.assess(report)
            if self.artifacts is not None:
                self.artifacts.append("evidence_reports.jsonl", report)
                self.artifacts.append("assurance_assessments.jsonl", assessment)
            assessments.append(assessment)
        return tuple(assessments)

    def record_ground_truth(self, payload: dict[str, Any]) -> None:
        if self.artifacts is not None:
            self.artifacts.append("ground_truth.jsonl", payload)

    def record_decision(self, payload: dict[str, Any]) -> None:
        if self.artifacts is not None:
            self.artifacts.append("decisions.jsonl", payload)

    def write_metrics(self, payload: dict[str, Any]) -> None:
        if self.artifacts is not None:
            self.artifacts._write_json(self.artifacts.directory / "metrics.json", payload)
