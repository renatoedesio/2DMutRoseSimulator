"""Executa visualmente uma decomposição Hospital no simulador."""

import argparse

from src.domains.hospital.domain import HospitalMissionDomain
from src.core.mission.agent_dispatcher import AgentMissionDispatcher
from src.core.mission.decomposition_reader import DecompositionReader
from src.core.mission.scenario_binder import ScenarioBinder
from src.core.mission.world_knowledge_reader import WorldKnowledgeReader
from src.scenarios import HOSPITAL_SCENARIO_1, HOSPITAL_SCENARIO_2
from src.core.simulator import Simulator


SCENARIOS = {"hospital-1": HOSPITAL_SCENARIO_1, "hospital-2": HOSPITAL_SCENARIO_2}


def main() -> None:
    parser = argparse.ArgumentParser(description="Executa uma missão Hospital no simulador.")
    parser.add_argument("mission_file")
    parser.add_argument("world_db")
    parser.add_argument("scenario", choices=SCENARIOS)
    arguments = parser.parse_args()

    scenario = SCENARIOS[arguments.scenario]
    mission = DecompositionReader().read(arguments.mission_file)
    world = WorldKnowledgeReader().read(arguments.world_db)
    bound_mission = ScenarioBinder().bind(mission, scenario, world)
    if not bound_mission.is_valid:
        for issue in bound_mission.issues:
            print(f"{issue.task_key}: {issue.message}")
        return

    simulator = Simulator(scenario)
    dispatcher = AgentMissionDispatcher(
        bound_mission, HospitalMissionDomain(world), simulator.environment, simulator.navigations
    )
    simulator.set_mission_dispatcher(dispatcher)
    simulator.run()


if __name__ == "__main__":
    main()
