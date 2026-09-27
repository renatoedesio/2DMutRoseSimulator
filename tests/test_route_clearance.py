import unittest
from pathlib import Path
import json

import yaml

from src.platforms.simulator2d.route_clearance import assess_route_clearance


class RouteClearanceTests(unittest.TestCase):
    def test_rejects_invalid_confidence(self) -> None:
        with self.assertRaises(ValueError):
            assess_route_clearance(None, (0, 0), (1, 1), 1, 0.01, confidence_level=1.0)

    def test_contract_limits_match_the_versioned_geometry_report(self) -> None:
        assurance_directory = (
            Path(__file__).resolve().parents[1]
            / "experiments"
            / "room_preparation"
            / "hospital"
            / "scenario_1"
            / "assurance"
        )
        contract = yaml.safe_load((assurance_directory / "contract.yaml").read_text(encoding="utf-8"))
        report = json.loads((assurance_directory / "reachability_geometry.json").read_text(encoding="utf-8"))

        for task_key, result in report["tasks"].items():
            criterion = contract["tasks"][task_key]["assumptions"][0]["criteria"]
            self.assertEqual(result["recommended_sigma_m"], criterion["max_localization_uncertainty"])


if __name__ == "__main__":
    unittest.main()
