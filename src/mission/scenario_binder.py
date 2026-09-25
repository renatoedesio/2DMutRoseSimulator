"""Resolve tokens externos da missão para entidades de um cenário."""

from src.mission.models import BoundMission, BoundTask, Mission, MissionTask, ValidationIssue
from src.mission.world_knowledge_reader import WorldKnowledge
from src.scenarios import Scenario


class ScenarioBinder:
    """Valida e liga uma missão a locais, papéis e capacidades do cenário."""

    def bind(
        self, mission: Mission, scenario: Scenario, world_knowledge: WorldKnowledge | None = None
    ) -> BoundMission:
        issues: list[ValidationIssue] = []
        bound_tasks: dict[str, BoundTask] = {}
        for task in mission.tasks.values():
            location_name = scenario.location_aliases.get(task.location_token)
            if location_name is None:
                issues.append(ValidationIssue(task.key, f"Local lógico não mapeado: {task.location_token}"))
            elif location_name not in scenario.location_colors:
                issues.append(ValidationIssue(task.key, f"Local do cenário não existe: {location_name}"))
            elif world_knowledge is not None and task.location_token not in world_knowledge.rooms:
                issues.append(ValidationIssue(task.key, f"Local não existe no World DB: {task.location_token}"))

            candidate_roles = self._candidate_roles(task, scenario)
            required_capabilities = self._required_capabilities(task, mission)
            candidates = tuple(
                robot.label
                for robot in scenario.robots
                if robot.role in candidate_roles and required_capabilities.issubset(robot.capabilities)
            )
            if not candidate_roles:
                issues.append(ValidationIssue(task.key, "Papel de robô não mapeado pela missão."))
            elif len(candidates) < task.robot_requirement.minimum:
                issues.append(
                    ValidationIssue(
                        task.key,
                        f"Robôs elegíveis insuficientes: requer {task.robot_requirement.minimum}, disponíveis {len(candidates)}.",
                    )
                )
            bound_tasks[task.key] = BoundTask(task, location_name, candidates)

        for decomposition in mission.decompositions:
            for task_key in decomposition:
                if task_key not in mission.tasks:
                    issues.append(ValidationIssue(task_key, "A decomposição referencia uma tarefa inexistente."))
        if world_knowledge is not None:
            for world_room_name in world_knowledge.rooms:
                mapped_location = scenario.location_aliases.get(world_room_name)
                if mapped_location is None or mapped_location not in scenario.location_colors:
                    issues.append(
                        ValidationIssue(
                            "World DB",
                            f"A sala {world_room_name} não está representada no cenário {scenario.identifier}.",
                        )
                    )
        return BoundMission(mission, bound_tasks, tuple(issues))

    @staticmethod
    def _candidate_roles(task: MissionTask, scenario: Scenario) -> tuple[str, ...]:
        robot_types = [value for value in task.arguments.values() if "robot" in value.casefold()]
        roles: list[str] = []
        for robot_type in robot_types:
            roles.extend(scenario.role_aliases.get(robot_type, ()))
        return tuple(dict.fromkeys(roles))

    @staticmethod
    def _required_capabilities(task: MissionTask, mission: Mission) -> frozenset[str]:
        return frozenset(
            mission.actions[action.name].capability
            for action in task.actions
            if action.name in mission.actions
        )
