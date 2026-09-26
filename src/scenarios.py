"""Catálogo de cenários disponíveis no simulador."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RobotDefinition:
    """Configuração inicial de um robô em um cenário."""

    label: str
    role: str
    start_position: tuple[float, float]
    color: tuple[int, int, int]
    capabilities: frozenset[str]
    battery_capacity: float = 100.0


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
    location_aliases: dict[str, str]
    role_aliases: dict[str, tuple[str, ...]]
    door_approaches: dict[str, tuple[int, int]] = field(default_factory=dict)
    door_positions: dict[str, tuple[int, int]] = field(default_factory=dict)


HOSPITAL_SCENARIO_1 = Scenario(
    identifier="hospital_scenario_1",
    asset_folder="hospital",
    title="Hospital — Cenário 1",
    location_colors={
        "RoomA": (52, 152, 219),
        "RoomB": (155, 89, 182),
        "RoomC": (230, 126, 34),
        "SanitizationRoom": (26, 188, 156),
        "Corredor_Principal": (46, 204, 113),
    },
    floor_color=(235, 241, 244),
    wall_color=(52, 73, 94),
    accent_color=(190, 210, 220),
    robots=(
        RobotDefinition("A-1", "Limpador", (70, 393), (52, 152, 219), frozenset({"cleaning", "door-opening", "sanitize"})),
        RobotDefinition("A-2", "Limpador", (115, 393), (52, 152, 219), frozenset({"cleaning", "door-opening", "sanitize"})),
        RobotDefinition("B-1", "Organizador", (160, 393), (155, 89, 182), frozenset({"moveobject"})),
        RobotDefinition("B-2", "Organizador", (205, 393), (155, 89, 182), frozenset({"moveobject"})),
    ),
    location_aliases={
        "RoomA": "RoomA",
        "RoomB": "RoomB",
        "RoomC": "RoomC",
        "SanitizationRoom": "SanitizationRoom",
    },
    role_aliases={"CleanerRobot": ("Limpador",), "robotteam": ("Organizador",)},
    door_approaches={
        "RoomA": (320, 393),
        "RoomB": (960, 393),
        "RoomC": (320, 393),
        "SanitizationRoom": (960, 393),
    },
    door_positions={
        "RoomA": (320, 340),
        "RoomB": (960, 340),
        "RoomC": (320, 460),
        "SanitizationRoom": (960, 460),
    },
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
        RobotDefinition("A-1", "Limpador", (70, 393), (52, 152, 219), frozenset({"cleaning", "door-opening", "sanitize"})),
        RobotDefinition("A-2", "Limpador", (115, 393), (52, 152, 219), frozenset({"cleaning", "door-opening", "sanitize"})),
        RobotDefinition("B-1", "Organizador", (160, 393), (155, 89, 182), frozenset({"moveobject"})),
    ),
    location_aliases=HOSPITAL_SCENARIO_1.location_aliases,
    role_aliases=HOSPITAL_SCENARIO_1.role_aliases,
    door_approaches=HOSPITAL_SCENARIO_1.door_approaches,
    door_positions=HOSPITAL_SCENARIO_1.door_positions,
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
    robots=(RobotDefinition("F-1", "Trabalhador", (90, 90), (230, 126, 34), frozenset({"cleaning", "moveobject"})),),
    location_aliases={"FarmA": "Campo", "Barn": "Galpao", "Storage": "Patio"},
    role_aliases={"FieldRobot": ("Trabalhador",), "robotteam": ("Trabalhador",)},
)

# Mantém compatibilidade com o inicializador anterior.
HOSPITAL = HOSPITAL_SCENARIO_1
