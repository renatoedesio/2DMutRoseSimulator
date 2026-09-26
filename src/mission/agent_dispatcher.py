"""Despacha uma decomposição validada para agentes do simulador."""

from dataclasses import dataclass

import pygame

from src.location import Location
from src.mission.executor import TimedMissionDomain
from src.mission.models import BoundMission, MissionTask
from src.robot import Robot, RobotState


@dataclass
class ActiveTask:
    task_key: str
    task: MissionTask
    robots: tuple[Robot, ...]
    action_index: int = 0
    remaining_seconds: float = 0.0


class AgentMissionDispatcher:
    """Conecta a sequência da missão às rotas e estados dos robôs."""

    MOVING_BATTERY_PER_SECOND = 1.0

    def __init__(self, bound_mission: BoundMission, domain: TimedMissionDomain, environment, navigations) -> None:
        self.bound_mission = bound_mission
        self.domain = domain
        self.environment = environment
        self.navigations = {navigation.context.robot.label: navigation for navigation in navigations}
        self.task_keys = bound_mission.mission.decompositions[0] if bound_mission.mission.decompositions else ()
        self.next_task_index = 0
        self.active_task: ActiveTask | None = None
        self.completed = False
        self.error_message: str | None = None

    @property
    def status_text(self) -> str:
        if self.error_message:
            return f"MISSÃO BLOQUEADA: {self.error_message}"
        if self.completed:
            return "MISSÃO CONCLUÍDA"
        if self.active_task is None:
            return "MISSÃO AGUARDANDO"
        return f"Tarefa {self.active_task.task_key}: {self.active_task.task.name}"

    def update(self, delta_time: float) -> None:
        if self.completed or self.error_message:
            return
        if self.active_task is None:
            self._start_next_task()
            return

        if any(navigation.error_message for navigation in self._active_navigations()):
            self._block("falha de navegação")
            return

        if any(robot.state == RobotState.MOVING for robot in self.active_task.robots):
            self._update_movement(delta_time)
            return
        if any(robot.state == RobotState.WAITING for robot in self.active_task.robots):
            if all(navigation.target is None for navigation in self._active_navigations()):
                self._start_action()
            return
        if all(robot.state == RobotState.ACTING for robot in self.active_task.robots):
            self._update_action(delta_time)

    def _start_next_task(self) -> None:
        if self.next_task_index >= len(self.task_keys):
            self.completed = True
            return
        task_key = self.task_keys[self.next_task_index]
        bound_task = self.bound_mission.tasks[task_key]
        robot_labels = bound_task.eligible_robot_labels[: bound_task.task.robot_requirement.minimum]
        robots = tuple(self.navigations[label].context.robot for label in robot_labels)
        errors = self.domain.validate_task(bound_task.task, robot_labels)
        if errors or not robots:
            self._block("; ".join(errors) or "sem robôs elegíveis")
            return
        location = self.environment.get_location_by_name(bound_task.location_name or "")
        if location is None:
            self._block(f"local indisponível: {bound_task.location_name}")
            return

        self.active_task = ActiveTask(task_key, bound_task.task, robots)
        for position_index, robot in enumerate(robots):
            robot.state = RobotState.MOVING
            robot.current_task = f"Ir para {location.name}"
            target = self._formation_target(location, position_index, len(robots), robot)
            self.navigations[robot.label].set_target(target)

    def _update_movement(self, delta_time: float) -> None:
        assert self.active_task is not None
        for robot in self.active_task.robots:
            navigation = self.navigations[robot.label]
            if navigation.target is None:
                robot.state = RobotState.WAITING
                robot.current_task = "Aguardando equipe"
            elif not robot.consume_battery(self.MOVING_BATTERY_PER_SECOND * delta_time):
                self._block(f"bateria esgotada: {robot.label}")

    def _start_action(self) -> None:
        assert self.active_task is not None
        action = self.active_task.task.actions[self.active_task.action_index]
        spec = self.domain.action_spec(action.name)
        for robot in self.active_task.robots:
            if robot.battery < spec.battery_cost:
                self._block(f"bateria insuficiente: {robot.label}")
                return
            robot.state = RobotState.ACTING
            robot.current_task = action.name
            robot.action_progress = 0.0
        self.active_task.remaining_seconds = spec.duration_seconds

    def _update_action(self, delta_time: float) -> None:
        assert self.active_task is not None
        action = self.active_task.task.actions[self.active_task.action_index]
        spec = self.domain.action_spec(action.name)
        self.active_task.remaining_seconds -= delta_time
        for robot in self.active_task.robots:
            robot.consume_battery(spec.battery_cost * delta_time / spec.duration_seconds)
            robot.action_progress = max(0.0, min(1.0, 1 - self.active_task.remaining_seconds / spec.duration_seconds))
        if self.active_task.remaining_seconds > 0:
            return

        labels = tuple(robot.label for robot in self.active_task.robots)
        try:
            self.domain.execute_action(action.name, self.active_task.task, labels)
        except ValueError as error:
            self._block(str(error))
            return
        self.active_task.action_index += 1
        if self.active_task.action_index < len(self.active_task.task.actions):
            self._start_action()
            return
        for robot in self.active_task.robots:
            robot.state = RobotState.IDLE
            robot.current_task = "Sem tarefa"
            robot.action_progress = 0.0
        self.next_task_index += 1
        self.active_task = None

    def _active_navigations(self):
        assert self.active_task is not None
        return [self.navigations[robot.label] for robot in self.active_task.robots]

    def _formation_target(
        self, location: Location, index: int, team_size: int, robot: Robot
    ) -> Location:
        """Escolhe posições próximas para que membros de uma equipe não se sobreponham."""
        if team_size == 1:
            return location

        offsets = [(-36, 0), (36, 0), (0, -36), (0, 36)]
        ordered_offsets = offsets[index:] + offsets[:index]
        for offset_x, offset_y in ordered_offsets:
            candidate = (location.center[0] + offset_x, location.center[1] + offset_y)
            same_location = self.environment.get_location(pygame.Vector2(candidate))
            if same_location == location and self.environment.is_walkable(*candidate, robot.radius):
                return Location(location.name, location.color, candidate)
        return location

    def _block(self, message: str) -> None:
        self.error_message = message
        if self.active_task:
            for robot in self.active_task.robots:
                robot.state = RobotState.BLOCKED
                robot.current_task = message
