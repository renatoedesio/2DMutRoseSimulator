"""Catálogo de cenários disponíveis no simulador."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RobotDefinition:
    """Configuração inicial de um robô em um cenário."""

    label: str
    role: str
    start_position: tuple[float, float]
    color: tuple[int, int, int]


@dataclass(frozen=True)
class Scenario:
    """Configuração visual, semântica e de agentes de um cenário."""

    identifier: str
    asset_folder: str
    title: str
    location_colors: dict[str, tuple[int, int, int]]
    floor_color: tuple[int, int, int]
    wall_color: tuple[int, int, int]
    accent_color: tuple[int, int, int]
    robots: tuple[RobotDefinition, ...]


HOSPITAL_SCENARIO_1 = Scenario(
    identifier="hospital_scenario_1",
    asset_folder="hospital",
    title="Hospital — Cenário 1",
    location_colors={
        "Sala_A": (52, 152, 219),
        "Sala_B": (155, 89, 182),
        "Corredor_Principal": (46, 204, 113),
    },
    floor_color=(235, 241, 244),
    wall_color=(52, 73, 94),
    accent_color=(190, 210, 220),
    robots=(
        RobotDefinition("A-1", "Limpador", (90, 90), (52, 152, 219)),
        RobotDefinition("A-2", "Limpador", (130, 90), (52, 152, 219)),
        RobotDefinition("B-1", "Organizador", (90, 170), (155, 89, 182)),
        RobotDefinition("B-2", "Organizador", (130, 170), (155, 89, 182)),
    ),
)

HOSPITAL_SCENARIO_2 = Scenario(
    identifier="hospital_scenario_2",
    asset_folder="hospital",
    title="Hospital — Cenário 2",
    location_colors=HOSPITAL_SCENARIO_1.location_colors,
    floor_color=(235, 241, 244),
    wall_color=(52, 73, 94),
    accent_color=(190, 210, 220),
    robots=(
        RobotDefinition("A-1", "Limpador", (90, 90), (52, 152, 219)),
        RobotDefinition("A-2", "Limpador", (130, 90), (52, 152, 219)),
        RobotDefinition("B-1", "Organizador", (90, 170), (155, 89, 182)),
    ),
)

FARM = Scenario(
    identifier="farm",
    asset_folder="farm",
    title="Fazenda",
    location_colors={
        "Galpao": (52, 152, 219),
        "Campo": (46, 204, 113),
        "Patio": (155, 89, 182),
    },
    floor_color=(235, 226, 190),
    wall_color=(109, 76, 65),
    accent_color=(204, 181, 116),
    robots=(RobotDefinition("F-1", "Trabalhador", (90, 90), (230, 126, 34)),),
)

# Mantém compatibilidade com o inicializador anterior.
HOSPITAL = HOSPITAL_SCENARIO_1
