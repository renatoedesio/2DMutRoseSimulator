"""Orquestrador genérico de missões, sem regras de um domínio específico."""

from dataclasses import dataclass
from typing import Protocol

from src.core.mission.models import BoundMission, MissionTask


class MissionDomain(Protocol):
    """Contrato que cada domínio implementa para executar suas próprias regras."""

    def validate_task(self, task: MissionTask, robot_labels: tuple[str, ...]) -> list[str]: ...

    def execute_action(self, action_name: str, task: MissionTask, robot_labels: tuple[str, ...]) -> str: ...


@dataclass(frozen=True)
class ActionSpec:
    duration_seconds: float
    battery_cost: float


class TimedMissionDomain(MissionDomain, Protocol):
    """Contrato extra para domínios que executam ações temporizadas no simulador."""

    def action_spec(self, action_name: str) -> ActionSpec: ...


@dataclass(frozen=True)
class ExecutionEvent:
    task_key: str
    action_name: str
    description: str


@dataclass(frozen=True)
class MissionExecution:
    completed: bool
    events: tuple[ExecutionEvent, ...]
    error: str | None = None


class MissionExecutor:
    """Executa a decomposição escolhida delegando semântica ao domínio."""

    def execute(
        self, bound_mission: BoundMission, domain: MissionDomain, decomposition_index: int = 0
    ) -> MissionExecution:
        if not bound_mission.is_valid:
            return MissionExecution(False, (), "A missão não passou na validação do cenário.")
        if decomposition_index >= len(bound_mission.mission.decompositions):
            return MissionExecution(False, (), "Índice de decomposição inválido.")

        events: list[ExecutionEvent] = []
        for task_key in bound_mission.mission.decompositions[decomposition_index]:
            bound_task = bound_mission.tasks[task_key]
            task = bound_task.task
            robot_labels = bound_task.eligible_robot_labels[: task.robot_requirement.minimum]
            errors = domain.validate_task(task, robot_labels)
            if errors:
                return MissionExecution(False, tuple(events), f"{task_key}: {'; '.join(errors)}")
            for action in task.actions:
                try:
                    description = domain.execute_action(action.name, task, robot_labels)
                except ValueError as error:
                    return MissionExecution(False, tuple(events), f"{task_key}: {error}")
                events.append(ExecutionEvent(task_key, action.name, description))
        return MissionExecution(True, tuple(events))
