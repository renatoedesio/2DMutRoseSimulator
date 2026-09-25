"""Carregamento do ambiente, colisões e busca de rotas A*."""

import heapq
import math
from pathlib import Path

import pygame

from src.location import Location
from src.scenarios import Scenario


class Environment:
    """Mapa renderizado e sua máscara colorida de colisão e locais."""

    PATH_GRID_SIZE = 8
    PATH_SAFETY_MARGIN = 6

    def __init__(self, asset_directory: Path, size: tuple[int, int], scenario: Scenario) -> None:
        self.size = size
        self.scenario = scenario
        self.location_colors = scenario.location_colors
        self.asset_directory = asset_directory
        self.map_path = asset_directory / "map.png"
        self.collision_path = asset_directory / "collision.png"

        self._create_example_assets_if_needed()
        self.map_image = pygame.image.load(self.map_path).convert()
        self.collision_mask = pygame.image.load(self.collision_path).convert()
        self.location_mask = self.collision_mask
        self._collision_obstacles = pygame.mask.from_threshold(
            self.collision_mask, (0, 0, 0, 255), (20, 20, 20, 255)
        )
        self._robot_masks: dict[int, pygame.mask.Mask] = {}

        if self.map_image.get_size() != self.collision_mask.get_size():
            raise ValueError("O mapa visual e a máscara combinada devem ter o mesmo tamanho.")

        self.size = self.map_image.get_size()
        self.locations = self._create_locations()
        self.injected_obstacles: list[tuple[tuple[int, int], int]] = []

    def _create_example_assets_if_needed(self) -> None:
        """Cria uma planta simples apenas quando o usuário ainda não forneceu imagens."""
        self.asset_directory.mkdir(parents=True, exist_ok=True)
        if self.map_path.exists() and self.collision_path.exists():
            return

        width, height = self.size
        visual = pygame.Surface((width, height))
        collision = pygame.Surface((width, height))
        if not self.map_path.exists():
            visual.fill(self.scenario.floor_color)
        if not self.collision_path.exists():
            collision.fill((255, 255, 255))

        wall_color = self.scenario.wall_color
        obstacles = [
            pygame.Rect(0, 0, width, 25),
            pygame.Rect(0, height - 25, width, 25),
            pygame.Rect(0, 0, 25, height),
            pygame.Rect(width - 25, 0, 25, height),
            pygame.Rect(180, 120, 360, 26),
            pygame.Rect(180, 120, 26, 220),
            pygame.Rect(514, 120, 26, 150),
            pygame.Rect(330, 420, 420, 26),
            pygame.Rect(724, 300, 26, 146),
        ]
        if not self.map_path.exists():
            for obstacle in obstacles:
                pygame.draw.rect(visual, wall_color, obstacle)
            pygame.draw.rect(visual, self.scenario.accent_color, (220, 165, 280, 135))
            pygame.draw.rect(visual, self.scenario.accent_color, (370, 465, 310, 95))
            pygame.image.save(visual, self.map_path)

        if not self.collision_path.exists():
            for obstacle in obstacles:
                pygame.draw.rect(collision, (0, 0, 0), obstacle)
            location_names = list(self.location_colors)
            pygame.draw.rect(collision, self.location_colors[location_names[2]], (30, 30, 900, 85))
            pygame.draw.rect(collision, self.location_colors[location_names[0]], (210, 150, 295, 175))
            pygame.draw.rect(collision, self.location_colors[location_names[1]], (355, 455, 355, 120))
            pygame.image.save(collision, self.collision_path)

    def is_walkable(self, x: float, y: float, radius: int) -> bool:
        """Retorna se o disco completo do robô não sobrepõe pixels pretos."""
        if (
            x - radius < 0
            or y - radius < 0
            or x + radius >= self.size[0]
            or y + radius >= self.size[1]
        ):
            return False

        robot_mask = self._get_robot_mask(radius)
        offset = (round(x) - radius, round(y) - radius)
        return self._collision_obstacles.overlap(robot_mask, offset) is None

    def find_path(
        self,
        origin: tuple[float, float] | pygame.Vector2,
        destination: tuple[float, float] | pygame.Vector2,
        robot_radius: int,
    ) -> list[tuple[float, float]]:
        """Calcula, com A*, uma rota navegável entre dois pontos do mapa.

        A busca ocorre em uma grade menor que a imagem para manter o simulador
        responsivo. Cada nó é validado contra a máscara considerando o raio do
        robô, portanto a rota mantém distância dos obstáculos pretos.
        """
        origin = pygame.Vector2(origin)
        destination = pygame.Vector2(destination)
        safe_radius = robot_radius + self.PATH_SAFETY_MARGIN
        if not self.is_walkable(destination.x, destination.y, safe_radius):
            return []

        start = self._nearest_walkable_cell(origin, safe_radius)
        goal = self._nearest_walkable_cell(destination, safe_radius)
        if start is None or goal is None:
            return []

        frontier: list[tuple[float, int, tuple[int, int]]] = []
        sequence = 0
        heapq.heappush(frontier, (0.0, sequence, start))
        came_from: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
        cost_so_far = {start: 0.0}
        walkable_cells: dict[tuple[int, int], bool] = {}

        while frontier:
            _, _, current = heapq.heappop(frontier)
            if current == goal:
                cells = self._reconstruct_path(came_from, goal)
                waypoints = [self._cell_to_point(cell) for cell in cells[1:]]
                waypoints.append((destination.x, destination.y))
                return self._simplify_path(origin, waypoints, safe_radius)

            for neighbor, step_cost in self._neighbors(current, safe_radius, walkable_cells):
                new_cost = cost_so_far[current] + step_cost
                if new_cost >= cost_so_far.get(neighbor, math.inf):
                    continue

                cost_so_far[neighbor] = new_cost
                priority = new_cost + self._heuristic(neighbor, goal)
                sequence += 1
                heapq.heappush(frontier, (priority, sequence, neighbor))
                came_from[neighbor] = current

        return []

    def add_injected_obstacle(self, center: tuple[int, int], radius: int = 26) -> None:
        """Desenha um obstáculo preto na máscara durante a execução.

        O mapa visual original não é alterado em disco; o círculo é desenhado
        sobre a tela e aplicado imediatamente à máscara de colisão em memória.
        """
        pygame.draw.circle(self.collision_mask, (0, 0, 0), center, radius)
        self._collision_obstacles = pygame.mask.from_threshold(
            self.collision_mask, (0, 0, 0, 255), (20, 20, 20, 255)
        )
        self.injected_obstacles.append((center, radius))

    def _get_robot_mask(self, radius: int) -> pygame.mask.Mask:
        if radius not in self._robot_masks:
            diameter = radius * 2 + 1
            surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
            pygame.draw.circle(surface, (255, 255, 255), (radius, radius), radius)
            self._robot_masks[radius] = pygame.mask.from_surface(surface)
        return self._robot_masks[radius]

    def is_route_clear(
        self,
        origin: pygame.Vector2,
        waypoints: list[pygame.Vector2],
        robot_radius: int,
    ) -> bool:
        """Verifica se todos os segmentos ainda estão livres na máscara atual."""
        safe_radius = robot_radius + self.PATH_SAFETY_MARGIN
        start = origin
        for waypoint in waypoints:
            if not self._has_clear_line(start, waypoint, safe_radius):
                return False
            start = waypoint
        return True

    def _nearest_walkable_cell(
        self, point: pygame.Vector2, robot_radius: int
    ) -> tuple[int, int] | None:
        base_cell = self._point_to_cell(point)
        for search_radius in range(8):
            for row in range(base_cell[1] - search_radius, base_cell[1] + search_radius + 1):
                for column in range(base_cell[0] - search_radius, base_cell[0] + search_radius + 1):
                    cell = (column, row)
                    cell_point = self._cell_to_point(cell)
                    if self.is_walkable(*cell_point, robot_radius):
                        return cell
        return None

    def _neighbors(
        self,
        cell: tuple[int, int],
        robot_radius: int,
        walkable_cells: dict[tuple[int, int], bool],
    ) -> list[tuple[tuple[int, int], float]]:
        neighbors: list[tuple[tuple[int, int], float]] = []
        for delta_x, delta_y in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            candidate = (cell[0] + delta_x, cell[1] + delta_y)
            if candidate not in walkable_cells:
                walkable_cells[candidate] = self.is_walkable(*self._cell_to_point(candidate), robot_radius)
            if not walkable_cells[candidate]:
                continue

            # Evita atravessar diagonalmente o canto de dois obstáculos.
            if delta_x and delta_y:
                side_a = (cell[0] + delta_x, cell[1])
                side_b = (cell[0], cell[1] + delta_y)
                for side in (side_a, side_b):
                    if side not in walkable_cells:
                        walkable_cells[side] = self.is_walkable(*self._cell_to_point(side), robot_radius)
                if not walkable_cells[side_a] or not walkable_cells[side_b]:
                    continue

            neighbors.append((candidate, math.sqrt(2) if delta_x and delta_y else 1.0))
        return neighbors

    def _point_to_cell(self, point: pygame.Vector2) -> tuple[int, int]:
        return (int(point.x // self.PATH_GRID_SIZE), int(point.y // self.PATH_GRID_SIZE))

    def _cell_to_point(self, cell: tuple[int, int]) -> tuple[float, float]:
        return (
            cell[0] * self.PATH_GRID_SIZE + self.PATH_GRID_SIZE / 2,
            cell[1] * self.PATH_GRID_SIZE + self.PATH_GRID_SIZE / 2,
        )

    @staticmethod
    def _heuristic(current: tuple[int, int], goal: tuple[int, int]) -> float:
        return math.dist(current, goal)

    @staticmethod
    def _reconstruct_path(
        came_from: dict[tuple[int, int], tuple[int, int] | None],
        current: tuple[int, int],
    ) -> list[tuple[int, int]]:
        path = [current]
        while came_from[current] is not None:
            current = came_from[current]  # type: ignore[assignment]
            path.append(current)
        return list(reversed(path))

    def _simplify_path(
        self,
        origin: pygame.Vector2,
        waypoints: list[tuple[float, float]],
        robot_radius: int,
    ) -> list[tuple[float, float]]:
        """Remove nós intermediários quando há linha de visão livre."""
        simplified: list[tuple[float, float]] = []
        current = origin
        index = 0
        while index < len(waypoints):
            last_visible = index
            for candidate_index in range(index, len(waypoints)):
                if self._has_clear_line(current, pygame.Vector2(waypoints[candidate_index]), robot_radius):
                    last_visible = candidate_index
                else:
                    break
            next_point = waypoints[last_visible]
            simplified.append(next_point)
            current = pygame.Vector2(next_point)
            index = last_visible + 1
        return simplified

    def _has_clear_line(self, start: pygame.Vector2, end: pygame.Vector2, robot_radius: int) -> bool:
        distance = start.distance_to(end)
        samples = max(1, math.ceil(distance / (self.PATH_GRID_SIZE / 2)))
        for step in range(1, samples + 1):
            point = start.lerp(end, step / samples)
            if not self.is_walkable(point.x, point.y, robot_radius):
                return False
        return True

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.map_image, (0, 0))
        for center, radius in self.injected_obstacles:
            pygame.draw.circle(screen, (0, 0, 0), center, radius)
            pygame.draw.circle(screen, (110, 110, 110), center, radius, 2)

    def _create_locations(self) -> list[Location]:
        """Lê regiões coloridas e deriva automaticamente seus centros."""
        locations = []
        for name, color in self.location_colors.items():
            region = pygame.mask.from_threshold(self.location_mask, (*color, 255), (1, 1, 1, 1))
            if region.count():
                locations.append(Location(name, color, region.centroid()))
        return locations

    def get_location(self, position: pygame.Vector2) -> Location | None:
        """Retorna o local definido pela cor do pixel sob o robô."""
        x, y = round(position.x), round(position.y)
        if not (0 <= x < self.size[0] and 0 <= y < self.size[1]):
            return None
        color = self.location_mask.get_at((x, y))[:3]
        return next((location for location in self.locations if location.color == color), None)

    def get_location_by_name(self, name: str) -> Location | None:
        """Localiza uma sala ou corredor ignorando maiúsculas e minúsculas."""
        normalized_name = name.strip().casefold()
        return next((location for location in self.locations if location.name.casefold() == normalized_name), None)
