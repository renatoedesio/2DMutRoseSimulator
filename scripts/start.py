"""Inicia uma missão catalogada pelo nome da família e do cenário."""

import argparse
from pathlib import Path

from src.domains.hospital.domain import HospitalMissionDomain
from src.core.mission.agent_dispatcher import AgentMissionDispatcher
from src.core.mission.catalog import MissionCatalog
from src.core.mission.decomposition_reader import DecompositionReader
from src.core.mission.scenario_binder import ScenarioBinder
from src.core.mission.world_knowledge_reader import WorldKnowledgeReader
from src.scenarios import HOSPITAL_SCENARIO_1, HOSPITAL_SCENARIO_2
from src.core.simulator import Simulator


SIMULATOR_SCENARIOS = {
    "hospital-1": HOSPITAL_SCENARIO_1,
    "hospital-2": HOSPITAL_SCENARIO_2,
}


def load_bundle_for_execution(family: str, scenario_name: str):
    """Carrega e valida um pacote, sem iniciar a janela do simulador."""
    project_directory = Path(__file__).resolve().parent.parent
    bundle = MissionCatalog(project_directory / "experiments").load(family, scenario_name)
    if bundle.domain != "hospital":
        raise ValueError(f"Domínio ainda não suportado pelo iniciador: {bundle.domain}")
    simulator_scenario = SIMULATOR_SCENARIOS[bundle.simulator_scenario]
    mission = DecompositionReader().read(bundle.decomposition_path)
    world = WorldKnowledgeReader().read(bundle.world_db_path)
    bound_mission = ScenarioBinder().bind(mission, simulator_scenario, world)
    return bundle, simulator_scenario, world, bound_mission


def main() -> None:
    parser = argparse.ArgumentParser(description="Inicia uma missão catalogada.")
    parser.add_argument("family", nargs="?", help="Família, por exemplo RoomPreparation")
    parser.add_argument("scenario", nargs="?", help="Cenário, por exemplo scenario_1")
    parser.add_argument("--list", action="store_true", help="Lista os pacotes disponíveis")
    parser.add_argument("--validate", action="store_true", help="Valida sem abrir o simulador")
    arguments = parser.parse_args()

    catalog = MissionCatalog(Path(__file__).resolve().parent.parent / "experiments")
    if arguments.list:
        for bundle in catalog.list():
            print(f"{bundle.family} {bundle.scenario_name} -> {bundle.simulator_scenario}")
        return
    if not arguments.family or not arguments.scenario:
        parser.error("Informe família e cenário, ou use --list.")

    try:
        bundle, simulator_scenario, world, bound_mission = load_bundle_for_execution(
            arguments.family, arguments.scenario
        )
    except (FileNotFoundError, ValueError, KeyError) as error:
        parser.error(str(error))
    if not bound_mission.is_valid:
        print("Pacote inválido:")
        for issue in bound_mission.issues:
            print(f"- {issue.task_key}: {issue.message}")
        return
    print(f"Pacote validado: {bundle.family}/{bundle.scenario_name}")
    if arguments.validate:
        return

    simulator = Simulator(simulator_scenario)
    dispatcher = AgentMissionDispatcher(
        bound_mission, HospitalMissionDomain(world), simulator.environment, simulator.navigations
    )
    simulator.set_mission_dispatcher(dispatcher)
    simulator.run()


if __name__ == "__main__":
    main()
