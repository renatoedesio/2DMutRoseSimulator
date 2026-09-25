"""Leitor de arquivos task_output.json sem dependência do simulador."""

import json
from pathlib import Path

from src.mission.models import (
    ActionDefinition,
    ActionStep,
    Mission,
    MissionConstraint,
    MissionTask,
    RobotRequirement,
)


class DecompositionReader:
    """Converte o JSON externo em modelos de missão tipados."""

    def read(self, path: str | Path) -> Mission:
        with Path(path).open(encoding="utf-8") as source:
            data = json.load(source)

        actions = {
            item["name"]: ActionDefinition(item["name"], item["capabilities"])
            for item in data.get("actions", [])
        }
        tasks = {key: self._read_task(key, value) for key, value in data.get("tasks", {}).items()}
        constraints = tuple(
            MissionConstraint(
                item["type"], item["task_instances"]["t0"], item["task_instances"]["t1"]
            )
            for item in data.get("constraints", [])
        )
        decompositions = tuple(tuple(task_keys) for task_keys in data.get("mission_decompositions", []))
        return Mission(actions, tasks, constraints, decompositions)

    def _read_task(self, key: str, data: dict) -> MissionTask:
        robot_count = data.get("robots_num", {})
        fixed = str(robot_count.get("fixed", "False")).casefold() == "true"
        minimum = int(robot_count.get("num", robot_count.get("min", 1)))
        maximum = minimum if fixed else int(robot_count["max"]) if "max" in robot_count else None
        actions = tuple(
            ActionStep(step["name"], step.get("arguments", ""))
            for step in data.get("decomposition", {}).values()
        )
        return MissionTask(
            key=key,
            task_id=data["id"],
            name=data["name"],
            location_token=data.get("locations", ""),
            arguments=data.get("arguments", {}),
            argument_values=data.get("arguments_values", {}),
            robot_requirement=RobotRequirement(fixed, minimum, maximum),
            actions=actions,
            preconditions=tuple(data["preconditions"]) if isinstance(data.get("preconditions"), list) else (),
            effects=tuple(data["effects"]) if isinstance(data.get("effects"), list) else (),
        )
