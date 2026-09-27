"""Deriva um sigma máximo recomendado a partir das rotas do Simulator2D."""

import argparse
import json
from pathlib import Path

import pygame

from src.core.environment import Environment
from src.core.mission.decomposition_reader import DecompositionReader
from src.core.mission.scenario_binder import ScenarioBinder
from src.core.mission.world_knowledge_reader import WorldKnowledgeReader
from src.core.simulator import Simulator
from src.platforms.simulator2d.route_clearance import assess_route_clearance
from src.scenarios import HOSPITAL_SCENARIO_1, HOSPITAL_SCENARIO_2


SCENARIOS = {"hospital-1": HOSPITAL_SCENARIO_1, "hospital-2": HOSPITAL_SCENARIO_2}


def main() -> None:
    parser = argparse.ArgumentParser(description="Analisa o clearance de rota para assumptions Reachability.")
    parser.add_argument("mission_file")
    parser.add_argument("world_db")
    parser.add_argument("scenario", choices=SCENARIOS)
    parser.add_argument("--confidence", type=float, default=0.95, help="Cobertura normal bicaudal (padrão: 0.95).")
    parser.add_argument("--output", type=Path, help="Arquivo JSON opcional para o relatório.")
    arguments = parser.parse_args()

    scenario = SCENARIOS[arguments.scenario]
    mission = DecompositionReader().read(arguments.mission_file)
    world = WorldKnowledgeReader().read(arguments.world_db)
    bound = ScenarioBinder().bind(mission, scenario, world)
    if not bound.is_valid:
        parser.error("Missão inválida para o cenário; execute mission_reader para detalhes.")

    pygame.init()
    pygame.display.set_mode((1, 1), flags=pygame.HIDDEN)
    try:
        project_directory = Path(__file__).resolve().parent.parent.parent
        environment = Environment(
            project_directory / "src" / "domains" / scenario.asset_folder / "assets",
            Simulator.WINDOW_SIZE,
            scenario,
        )
        robots = {robot.label: robot for robot in scenario.robots}
        results = {}
        for task_key, bound_task in bound.tasks.items():
            if not bound_task.eligible_robot_labels or bound_task.location_name is None:
                continue
            robot = robots[bound_task.eligible_robot_labels[0]]
            target = environment.get_location_by_name(bound_task.location_name)
            if target is None:
                continue
            first_action = bound_task.task.actions[0].name if bound_task.task.actions else ""
            destination = environment.get_door_approach(target.name) if first_action == "open-door" else target.center
            if destination is None:
                destination = target.center
            results[task_key] = assess_route_clearance(
                environment,
                robot.start_position,
                destination,
                robot_radius_px=16,
                meters_per_pixel=scenario.meters_per_pixel,
                confidence_level=arguments.confidence,
            ).to_dict()
    finally:
        pygame.quit()

    payload = {
        "scenario": scenario.identifier,
        "meters_per_pixel": scenario.meters_per_pixel,
        "robot_radius_m": 16 * scenario.meters_per_pixel,
        "navigation_safety_margin_m": Environment.PATH_SAFETY_MARGIN * scenario.meters_per_pixel,
        "confidence_level": arguments.confidence,
        "tasks": results,
        "method_note": "Static estimate from each eligible robot's initial pose to its task's first action target.",
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    if arguments.output:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
