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
        self.action_progress = 0.0

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
        battery_box = pygame.Rect(label_box.left, label_box.bottom + 2, label_box.width, 5)
        battery_level = self.battery / self.battery_capacity if self.battery_capacity else 0.0
        battery_level = max(0.0, min(1.0, battery_level))
        pygame.draw.rect(screen, (80, 90, 95), battery_box, border_radius=2)
        if battery_level > 0:
            battery_fill = battery_box.copy()
            battery_fill.width = round(battery_box.width * battery_level)
            pygame.draw.rect(screen, (46, 204, 113), battery_fill, border_radius=2)
        if self.state == RobotState.ACTING:
            progress_box = pygame.Rect(label_box.left, battery_box.bottom + 2, label_box.width, 5)
            pygame.draw.rect(screen, (80, 90, 95), progress_box, border_radius=2)
            if self.action_progress > 0:
                progress_fill = progress_box.copy()
                progress_fill.width = round(progress_box.width * self.action_progress)
                pygame.draw.rect(screen, (231, 76, 60), progress_fill, border_radius=2)

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
