"""Modelos independentes do Pygame para decomposições de missão."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ActionDefinition:
    name: str
    capability: str


@dataclass(frozen=True)
class ActionStep:
    name: str
    arguments: str


@dataclass(frozen=True)
class RobotRequirement:
    fixed: bool
    minimum: int
    maximum: int | None


@dataclass(frozen=True)
class MissionTask:
    key: str
    task_id: str
    name: str
    location_token: str
    arguments: dict[str, str]
    argument_values: dict[str, str]
    robot_requirement: RobotRequirement
    actions: tuple[ActionStep, ...]
    preconditions: tuple[dict, ...]
    effects: tuple[dict, ...]


@dataclass(frozen=True)
class MissionConstraint:
    constraint_type: str
    first_task: str
    second_task: str


@dataclass(frozen=True)
class Mission:
    actions: dict[str, ActionDefinition]
    tasks: dict[str, MissionTask]
    constraints: tuple[MissionConstraint, ...]
    decompositions: tuple[tuple[str, ...], ...]


@dataclass(frozen=True)
class ValidationIssue:
    task_key: str
    message: str


@dataclass(frozen=True)
class BoundTask:
    task: MissionTask
    location_name: str | None
    eligible_robot_labels: tuple[str, ...]


@dataclass(frozen=True)
class BoundMission:
    mission: Mission
    tasks: dict[str, BoundTask]
    issues: tuple[ValidationIssue, ...]

    @property
    def is_valid(self) -> bool:
        return not self.issues
