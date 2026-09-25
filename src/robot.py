"""Representação física e estado operacional de um robô."""

from enum import Enum

import pygame

from src.environment import Environment
from src.scenarios import RobotDefinition


class RobotState(str, Enum):
    IDLE = "IDLE"
    MOVING = "MOVING"
    WAITING = "WAITING"
    ACTING = "ACTING"
    BLOCKED = "BLOCKED"


class Robot:
    """Robô circular que desliza pelos espaços permitidos da máscara."""

    def __init__(self, definition: RobotDefinition) -> None:
        self.label = definition.label
        self.role = definition.role
        self.position = pygame.Vector2(definition.start_position)
        self.radius = 16
        self.speed = 220.0
        self.color = definition.color
        self.battery_capacity = definition.battery_capacity
        self.battery = definition.battery_capacity
        self.state = RobotState.IDLE
        self.current_task = "Sem tarefa"

    def move_towards(
        self, target: pygame.Vector2, delta_time: float, environment: Environment
    ) -> bool:
        """Move fisicamente até um waypoint e informa se ele foi alcançado."""
        offset = target - self.position
        distance = offset.length()
        max_distance = self.speed * delta_time
        if distance <= max_distance:
            if environment.is_walkable(target.x, target.y, self.radius):
                self.position = target
                return True
            return False

        movement = offset.normalize() * max_distance
        candidate = self.position + movement
        if environment.is_walkable(candidate.x, candidate.y, self.radius):
            self.position = candidate
        return False

    def draw(self, screen: pygame.Surface, font: pygame.font.Font, selected: bool) -> None:
        center = (round(self.position.x), round(self.position.y))
        pygame.draw.circle(screen, self.color, center, self.radius)
        border_color = (241, 196, 15) if selected else (255, 255, 255)
        border_width = 4 if selected else 2
        pygame.draw.circle(screen, border_color, center, self.radius, border_width)
        label = font.render(self.label, True, (20, 35, 45))
        label_box = label.get_rect(midbottom=(center[0], center[1] - self.radius - 5)).inflate(6, 4)
        pygame.draw.rect(screen, (255, 255, 255), label_box, border_radius=3)
        self._blit_centered(screen, label, label_box.center)

    @staticmethod
    def _blit_centered(screen: pygame.Surface, image: pygame.Surface, center: tuple[int, int]) -> None:
        screen.blit(image, image.get_rect(center=center))

    def consume_battery(self, amount: float) -> bool:
        """Consome bateria e retorna se ainda há carga disponível."""
        self.battery = max(0.0, self.battery - amount)
        return self.battery > 0.0

    def draw_route(
        self,
        screen: pygame.Surface,
        waypoints: list[pygame.Vector2],
        target: pygame.Vector2 | None,
    ) -> None:
        """Desenha a rota A* atual e o ponto de destino para depuração."""
        route_points = [self.position, *waypoints]
        if len(route_points) > 1:
            pygame.draw.lines(screen, (231, 76, 60), False, route_points, 3)
        if target is not None:
            pygame.draw.circle(screen, (231, 76, 60), target, 7, 2)
