import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.integration.assurance_runtime import AssuranceRuntime, RunArtifacts


class AssuranceRuntimeTests(unittest.TestCase):
    def test_reachability_is_assessed_and_logged_separately(self) -> None:
        contract = (
            Path(__file__).resolve().parents[1]
            / "experiments"
            / "room_preparation"
            / "hospital"
            / "scenario_1"
            / "assurance"
            / "contract.yaml"
        )
        with TemporaryDirectory() as temporary_directory:
            artifacts = RunArtifacts.create(
                Path(temporary_directory), "RoomPreparation", "hospital", "scenario_1", contract
            )
            runtime = AssuranceRuntime(contract, artifacts)
            runtime.validate_tasks({"t1"})
            assessment = runtime.assess_reachability(
                "t1", "AVAILABLE", localization_sigma_m=0.0, measured_position_m=(1.0, 2.0)
            )[0]
            runtime.record_ground_truth({"task_id": "t1", "position": {"x": 1, "y": 2}})
            runtime.record_decision({"task_id": "t1", "response_type": "continue"})
            runtime.write_metrics({"completed": True})

            self.assertEqual("SATISFIED", assessment.verdict)
            evidence = json.loads((artifacts.directory / "evidence_reports.jsonl").read_text(encoding="utf-8"))
            ground_truth = json.loads((artifacts.directory / "ground_truth.jsonl").read_text(encoding="utf-8"))
            self.assertEqual("AVAILABLE", evidence["payload"]["path_status"])
            self.assertEqual({"x": 1, "y": 2}, ground_truth["position"])
            self.assertTrue((artifacts.directory / "assurance_assessments.jsonl").exists())
            self.assertTrue((artifacts.directory / "decisions.jsonl").exists())
            self.assertTrue((artifacts.directory / "metrics.json").exists())


if __name__ == "__main__":
    unittest.main()
