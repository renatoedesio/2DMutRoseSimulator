"""Regras Hospital para predicados e ações da decomposição de missão."""

from dataclasses import dataclass

from src.core.mission.models import MissionTask
from src.core.mission.executor import ActionSpec
from src.core.mission.world_knowledge_reader import WorldKnowledge


@dataclass
class HospitalRoomState:
    is_clean: bool
    is_prepared: bool
    door_open: bool
    door_operational: bool = True
    accessible: bool = True
    alternate_access: bool = False
    standard_cleaning_available: bool = True
    backup_cleaning_available: bool = False
    standard_organization_available: bool = True
    alternative_organization_available: bool = False


class HospitalMissionDomain:
    """Executa somente as regras que pertencem ao Hospital."""

    def __init__(self, world_knowledge: WorldKnowledge) -> None:
        self._initial_rooms = {
            name: HospitalRoomState(
                room.is_clean, room.is_prepared, room.door_open, room.door_operational, room.accessible, room.alternate_access,
                room.standard_cleaning_available, room.backup_cleaning_available,
                room.standard_organization_available, room.alternative_organization_available
            )
            for name, room in world_knowledge.rooms.items()
        }
        self.rooms: dict[str, HospitalRoomState] = {}
        self.robot_sanitized: dict[str, bool] = {}
        self.reset()

    def reset(self) -> None:
        """Restaura as condições iniciais das salas e dos robôs."""
        self.rooms = {
            name: HospitalRoomState(
                room.is_clean, room.is_prepared, room.door_open, room.door_operational, room.accessible, room.alternate_access,
                room.standard_cleaning_available, room.backup_cleaning_available,
                room.standard_organization_available, room.alternative_organization_available
            )
            for name, room in self._initial_rooms.items()
        }
        self.robot_sanitized.clear()

    def validate_task(self, task: MissionTask, robot_labels: tuple[str, ...]) -> list[str]:
        errors = []
        for precondition in task.preconditions:
            predicate = precondition.get("predicate", "")
            if not self._evaluate_predicate(predicate, robot_labels):
                errors.append(f"pré-condição não satisfeita: {predicate}")
        return errors

    def inject_fault(self, fault_name: str, room_name: str) -> None:
        room = self.rooms.get(room_name)
        if room is None:
            raise ValueError(f"sala Hospital nao encontrada: {room_name}")
        if fault_name == "door_jammed":
            room.door_operational = False
            room.door_open = False
            room.accessible = False
            return
        raise ValueError(f"falha Hospital nao suportada: {fault_name}")

    def action_spec(self, action_name: str) -> ActionSpec:
        specs = {
            "open-door": ActionSpec(2.0, 2.0),
            "clean-room": ActionSpec(5.0, 12.0),
            "clean-room-alternative": ActionSpec(6.0, 14.0),
            "clean-room-backup": ActionSpec(7.0, 16.0),
            "sanitize-robot": ActionSpec(4.0, 4.0),
            "move-furniture": ActionSpec(8.0, 15.0),
            "move-furniture-alternative": ActionSpec(10.0, 18.0),
        }
        if action_name not in specs:
            raise ValueError(f"ação Hospital sem duração configurada: {action_name}")
        return specs[action_name]

    def execute_action(self, action_name: str, task: MissionTask, robot_labels: tuple[str, ...]) -> str:
        room = self._room_for(task)
        if action_name == "open-door":
            if not room.door_operational:
                raise ValueError("porta inoperante")
            room.door_open = True
            return f"porta de {task.location_token} aberta"
        if action_name == "clean-room":
            if not room.door_open:
                raise ValueError("a porta precisa estar aberta antes da limpeza")
            room.is_clean = True
            for robot_label in robot_labels:
                self.robot_sanitized[robot_label] = False
            return f"{task.location_token} limpo por {', '.join(robot_labels)}"
        if action_name == "clean-room-alternative":
            if not room.alternate_access:
                raise ValueError("acesso alternativo indisponivel")
            room.is_clean = True
            for robot_label in robot_labels:
                self.robot_sanitized[robot_label] = False
            return f"{task.location_token} limpo pelo acesso alternativo por {', '.join(robot_labels)}"
        if action_name == "sanitize-robot":
            for robot_label in robot_labels:
                self.robot_sanitized[robot_label] = True
            return f"robôs sanitizados em {task.location_token}: {', '.join(robot_labels)}"
        if action_name == "move-furniture":
            room.is_prepared = True
            return f"móveis organizados em {task.location_token} por {', '.join(robot_labels)}"
        raise ValueError(f"ação Hospital não suportada: {action_name}")

    def room_summary(self) -> list[str]:
        return [
            f"{name}: clean={state.is_clean}, prepared={state.is_prepared}, door_open={state.door_open}"
            for name, state in self.rooms.items()
        ]

    def is_door_open(self, room_name: str) -> bool:
        """Informa se a porta da sala está aberta para a visualização."""
        room = self.rooms.get(room_name)
        return room.door_open if room is not None else False

    def room_statuses(self) -> list[tuple[str, bool, bool, bool]]:
        """Fornece o estado das salas para o painel do simulador."""
        return [
            (name, state.door_open, state.is_clean, state.is_prepared)
            for name, state in self.rooms.items()
        ]

    def _evaluate_predicate(self, predicate: str, robot_labels: tuple[str, ...]) -> bool:
        negated = predicate.startswith("not ")
        expression = predicate.removeprefix("not ")
        subject, _, property_name = expression.partition(".")
        if subject.startswith("?"):
            value = all(self.robot_sanitized.get(label, False) for label in robot_labels)
        else:
            room = self.rooms.get(subject)
            if room is None or not hasattr(room, property_name):
                return False
            value = bool(getattr(room, property_name))
        return not value if negated else value

    def _room_for(self, task: MissionTask) -> HospitalRoomState:
        room = self.rooms.get(task.location_token)
        if room is None:
            raise ValueError(f"sala Hospital não encontrada: {task.location_token}")
        return room
