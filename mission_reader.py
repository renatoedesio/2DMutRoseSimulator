"""Examina uma decomposição externa para um cenário sem iniciar o Pygame."""

import argparse

from src.mission.decomposition_reader import DecompositionReader
from src.mission.scenario_binder import ScenarioBinder
from src.mission.world_knowledge_reader import WorldKnowledgeReader
from src.scenarios import FARM, HOSPITAL_SCENARIO_1, HOSPITAL_SCENARIO_2


SCENARIOS = {
    "hospital-1": HOSPITAL_SCENARIO_1,
    "hospital-2": HOSPITAL_SCENARIO_2,
    "farm": FARM,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Lê e valida uma decomposição de missão.")
    parser.add_argument("mission_file", help="Caminho do task_output.json")
    parser.add_argument("scenario", choices=SCENARIOS, help="Cenário que receberá a missão")
    parser.add_argument("--world-db", help="Caminho opcional para o World_db.xml")
    arguments = parser.parse_args()

    mission = DecompositionReader().read(arguments.mission_file)
    world_knowledge = WorldKnowledgeReader().read(arguments.world_db) if arguments.world_db else None
    bound_mission = ScenarioBinder().bind(mission, SCENARIOS[arguments.scenario], world_knowledge)
    print(f"Tarefas lidas: {len(mission.tasks)}")
    print(f"Decomposições disponíveis: {len(mission.decompositions)}")
    if world_knowledge is not None:
        print(f"Salas carregadas do World DB: {', '.join(world_knowledge.rooms)}")
    for task_key, task in bound_mission.tasks.items():
        print(f"{task_key}: {task.task.name} -> {task.location_name or 'NÃO MAPEADO'} | robôs: {', '.join(task.eligible_robot_labels) or 'nenhum'}")
    if bound_mission.is_valid:
        print("Missão válida para o cenário.")
    else:
        print("Missão não está pronta para execução:")
        for issue in bound_mission.issues:
            print(f"- {issue.task_key}: {issue.message}")


if __name__ == "__main__":
    main()
