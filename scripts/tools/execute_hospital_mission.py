"""Executa uma decomposição no domínio Hospital sem iniciar o Pygame."""

import argparse

from src.domains.hospital.domain import HospitalMissionDomain
from src.core.mission.decomposition_reader import DecompositionReader
from src.core.mission.executor import MissionExecutor
from src.core.mission.scenario_binder import ScenarioBinder
from src.core.mission.world_knowledge_reader import WorldKnowledgeReader
from src.scenarios import HOSPITAL_SCENARIO_1, HOSPITAL_SCENARIO_2


SCENARIOS = {"hospital-1": HOSPITAL_SCENARIO_1, "hospital-2": HOSPITAL_SCENARIO_2}


def main() -> None:
    parser = argparse.ArgumentParser(description="Executa uma missão no domínio Hospital.")
    parser.add_argument("mission_file")
    parser.add_argument("world_db")
    parser.add_argument("scenario", choices=SCENARIOS)
    arguments = parser.parse_args()

    mission = DecompositionReader().read(arguments.mission_file)
    world = WorldKnowledgeReader().read(arguments.world_db)
    bound_mission = ScenarioBinder().bind(mission, SCENARIOS[arguments.scenario], world)
    domain = HospitalMissionDomain(world)
    execution = MissionExecutor().execute(bound_mission, domain)
    for event in execution.events:
        print(f"{event.task_key} / {event.action_name}: {event.description}")
    if execution.completed:
        print("Missão Hospital concluída.")
    else:
        print(f"Missão Hospital interrompida: {execution.error}")
    print("Estado final das salas:")
    for room_state in domain.room_summary():
        print(f"- {room_state}")


if __name__ == "__main__":
    main()
