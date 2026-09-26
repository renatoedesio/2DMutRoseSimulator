"""Behavior Tree responsável pela navegação autônoma do robô."""

from dataclasses import dataclass, field

import pygame
import py_trees

from src.core.environment import Environment
from src.core.location import Location
from src.core.robot import Robot


@dataclass
class NavigationContext:
    """Estado efêmero compartilhado entre os nós da árvore."""

    robot: Robot
    environment: Environment
    delta_time: float = 0.0
    waypoints: list[pygame.Vector2] = field(default_factory=list)
    error_message: str | None = None


class CheckReachability(py_trees.behaviour.Behaviour):
    """Verifica o contrato de alcançabilidade por meio da rota A*."""

    def __init__(self, context: NavigationContext) -> None:
        super().__init__(name="CheckReachability")
        self.context = context
        self.blackboard = self.attach_blackboard_client(
            name=f"Reachability {context.robot.label}", namespace=context.robot.label
        )
        self.blackboard.register_key(key="target_location", access=py_trees.common.Access.READ)
        self.blackboard.register_key(key="contract_status", access=py_trees.common.Access.WRITE)

    def update(self) -> py_trees.common.Status:
        target = self.blackboard.target_location
        if target is None:
            if self.blackboard.contract_status != "REACHED":
                self.blackboard.contract_status = "IDLE"
            return py_trees.common.Status.FAILURE

        if self.context.waypoints:
            if not self.context.environment.is_route_clear(
                self.context.robot.position, self.context.waypoints, self.context.robot.radius
            ):
                self.context.waypoints.clear()
                self.blackboard.contract_status = "VIOLATED"
                self.feedback_message = "Rota ativa bloqueada por obstáculo"
                return py_trees.common.Status.FAILURE
            return py_trees.common.Status.SUCCESS

        route = self.context.environment.find_path(
            self.context.robot.position, target.center, self.context.robot.radius
        )
        if not route:
            self.context.waypoints.clear()
            self.blackboard.contract_status = "VIOLATED"
            self.feedback_message = f"Sem rota para {target.name}"
            return py_trees.common.Status.FAILURE

        self.context.waypoints = [pygame.Vector2(point) for point in route]
        self.blackboard.contract_status = "VALID"
        self.feedback_message = f"Rota válida para {target.name}"
        return py_trees.common.Status.SUCCESS


class MoveToTarget(py_trees.behaviour.Behaviour):
    """Move o robô por cada waypoint enquanto o contrato continua válido."""

    def __init__(self, context: NavigationContext) -> None:
        super().__init__(name="MoveToTarget")
        self.context = context
        self.blackboard = self.attach_blackboard_client(
            name=f"Movement {context.robot.label}", namespace=context.robot.label
        )
        self.blackboard.register_key(key="target_location", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key(key="contract_status", access=py_trees.common.Access.WRITE)

    def update(self) -> py_trees.common.Status:
        if not self.context.waypoints:
            self.blackboard.target_location = None
            self.blackboard.contract_status = "REACHED"
            return py_trees.common.Status.SUCCESS

        waypoint = self.context.waypoints[0]
        previous_position = self.context.robot.position.copy()
        reached_waypoint = self.context.robot.move_towards(
            waypoint, self.context.delta_time, self.context.environment
        )
        if self.context.robot.position == previous_position and not reached_waypoint:
            self.blackboard.contract_status = "VIOLATED"
            self.feedback_message = "Movimento bloqueado pela máscara de colisão"
            return py_trees.common.Status.FAILURE

        if reached_waypoint:
            self.context.waypoints.pop(0)
            if not self.context.waypoints:
                self.blackboard.target_location = None
                self.blackboard.contract_status = "REACHED"
                return py_trees.common.Status.SUCCESS

        return py_trees.common.Status.RUNNING


class AbortMovement(py_trees.behaviour.Behaviour):
    """Fallback que interrompe a navegação e comunica uma violação."""

    def __init__(self, context: NavigationContext) -> None:
        super().__init__(name="AbortMovement")
        self.context = context
        self.blackboard = self.attach_blackboard_client(
            name=f"Abort {context.robot.label}", namespace=context.robot.label
        )
        self.blackboard.register_key(key="target_location", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key(key="contract_status", access=py_trees.common.Access.READ)

    def update(self) -> py_trees.common.Status:
        if self.blackboard.contract_status == "VIOLATED":
            self.context.waypoints.clear()
            self.context.error_message = "ERRO: contrato de alcançabilidade VIOLATED"
            self.blackboard.target_location = None
            self.feedback_message = self.context.error_message
            print(self.context.error_message)
        return py_trees.common.Status.RUNNING


class NavigationController:
    """Expõe uma Behavior Tree de navegação para o ciclo do simulador."""

    def __init__(self, robot: Robot, environment: Environment) -> None:
        self.context = NavigationContext(robot=robot, environment=environment)
        self.blackboard = py_trees.blackboard.Client(
            name=f"Simulator {robot.label}", namespace=robot.label
        )
        self.blackboard.register_key(key="target_location", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key(key="contract_status", access=py_trees.common.Access.WRITE)
        self.blackboard.target_location = None
        self.blackboard.contract_status = "IDLE"

        navigate = py_trees.composites.Sequence(
            name="NavigateToTarget",
            memory=False,
            children=[CheckReachability(self.context), MoveToTarget(self.context)],
        )
        fallback = AbortMovement(self.context)
        root = py_trees.composites.Selector(
            name="NavigationFallback",
            memory=False,
            children=[navigate, fallback],
        )
        self.tree = py_trees.trees.BehaviourTree(root)

    @property
    def target(self) -> Location | None:
        return self.blackboard.target_location

    @property
    def waypoints(self) -> list[pygame.Vector2]:
        return self.context.waypoints

    @property
    def error_message(self) -> str | None:
        return self.context.error_message

    def set_target(self, location: Location) -> None:
        """Escreve o destino no Blackboard e reinicia a árvore para nova rota."""
        self.blackboard.target_location = location
        self.blackboard.contract_status = "PENDING"
        self.context.waypoints.clear()
        self.context.error_message = None
        self.tree.root.stop(py_trees.common.Status.INVALID)

    def set_target_point(self, point: tuple[int, int]) -> None:
        """Cria um destino lógico temporário para um clique no mapa."""
        self.set_target(Location("Destino selecionado", (0, 0, 0), point))

    def reset(self) -> None:
        """Cancela a rota e limpa qualquer erro de navegação."""
        self.blackboard.target_location = None
        self.blackboard.contract_status = "IDLE"
        self.context.waypoints.clear()
        self.context.error_message = None
        self.tree.root.stop(py_trees.common.Status.INVALID)

    def tick(self, delta_time: float) -> None:
        self.context.delta_time = delta_time
        self.tree.root.tick_once()
