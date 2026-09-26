"""Regras Hospital para predicados e ações da decomposição de missão."""

from dataclasses import dataclass

from src.mission.models import MissionTask
from src.mission.executor import ActionSpec
from src.mission.world_knowledge_reader import WorldKnowledge


@dataclass
class HospitalRoomState:
    is_clean: bool
    is_prepared: bool
    door_open: bool


class HospitalMissionDomain:
    """Executa somente as regras que pertencem ao Hospital."""

    def __init__(self, world_knowledge: WorldKnowledge) -> None:
        self._initial_rooms = {
            name: HospitalRoomState(room.is_clean, room.is_prepared, room.door_open)
            for name, room in world_knowledge.rooms.items()
        }
        self.rooms: dict[str, HospitalRoomState] = {}
        self.robot_sanitized: dict[str, bool] = {}
        self.reset()

    def reset(self) -> None:
        """Restaura as condições iniciais das salas e dos robôs."""
        self.rooms = {
            name: HospitalRoomState(room.is_clean, room.is_prepared, room.door_open)
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

    def action_spec(self, action_name: str) -> ActionSpec:
        specs = {
            "open-door": ActionSpec(2.0, 2.0),
            "clean-room": ActionSpec(5.0, 12.0),
            "sanitize-robot": ActionSpec(4.0, 4.0),
            "move-furniture": ActionSpec(8.0, 15.0),
        }
        if action_name not in specs:
            raise ValueError(f"ação Hospital sem duração configurada: {action_name}")
        return specs[action_name]

    def execute_action(self, action_name: str, task: MissionTask, robot_labels: tuple[str, ...]) -> str:
        room = self._room_for(task)
        if action_name == "open-door":
            room.door_open = True
            return f"porta de {task.location_token} aberta"
        if action_name == "clean-room":
            if not room.door_open:
                raise ValueError("a porta precisa estar aberta antes da limpeza")
            room.is_clean = True
            for robot_label in robot_labels:
                self.robot_sanitized[robot_label] = False
            return f"{task.location_token} limpo por {', '.join(robot_labels)}"
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
