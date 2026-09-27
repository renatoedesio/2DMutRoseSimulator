"""Derivação geométrica de um limite de incerteza para rotas 2D."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from statistics import NormalDist

import pygame

from src.core.environment import Environment


@dataclass(frozen=True)
class RouteClearanceAssessment:
    route_found: bool
    minimum_center_clearance_m: float | None
    operational_error_budget_m: float | None
    recommended_sigma_m: float | None
    confidence_level: float
    confidence_multiplier: float
    bottleneck_position_m: tuple[float, float] | None

    def to_dict(self) -> dict:
        return asdict(self)


def assess_route_clearance(
    environment: Environment,
    origin: tuple[float, float],
    destination: tuple[float, float],
    robot_radius_px: int,
    meters_per_pixel: float,
    *,
    safety_margin_px: int | None = None,
    confidence_level: float = 0.95,
    sample_spacing_px: float = 4.0,
) -> RouteClearanceAssessment:
    """Calcula o orçamento de erro a partir do gargalo geométrico da rota.

    ``sigma_max`` é calculado por ``budget / k``, onde ``k`` é o quantil
    bicaudal normal correspondente ao nível de confiança informado.
    """
    if not 0 < confidence_level < 1:
        raise ValueError("confidence_level deve estar entre 0 e 1.")
    if meters_per_pixel <= 0 or sample_spacing_px <= 0:
        raise ValueError("A escala e o espaçamento devem ser positivos.")
    margin_px = Environment.PATH_SAFETY_MARGIN if safety_margin_px is None else safety_margin_px
    route = environment.find_path(origin, destination, robot_radius_px)
    multiplier = NormalDist().inv_cdf((1 + confidence_level) / 2)
    if not route:
        return RouteClearanceAssessment(False, None, None, None, confidence_level, multiplier, None)

    points = _sample_route(origin, route, sample_spacing_px)
    bottleneck = min(points, key=lambda point: _maximum_walkable_radius(environment, point))
    center_clearance_px = _maximum_walkable_radius(environment, bottleneck)
    budget_px = max(0, center_clearance_px - robot_radius_px - margin_px)
    return RouteClearanceAssessment(
        route_found=True,
        minimum_center_clearance_m=center_clearance_px * meters_per_pixel,
        operational_error_budget_m=budget_px * meters_per_pixel,
        recommended_sigma_m=(budget_px * meters_per_pixel) / multiplier,
        confidence_level=confidence_level,
        confidence_multiplier=multiplier,
        bottleneck_position_m=(bottleneck.x * meters_per_pixel, bottleneck.y * meters_per_pixel),
    )


def _sample_route(
    origin: tuple[float, float], route: list[tuple[float, float]], spacing_px: float
) -> list[pygame.Vector2]:
    points: list[pygame.Vector2] = []
    start = pygame.Vector2(origin)
    for destination in route:
        end = pygame.Vector2(destination)
        distance = start.distance_to(end)
        steps = max(1, math.ceil(distance / spacing_px))
        points.extend(start.lerp(end, step / steps) for step in range(steps + 1))
        start = end
    return points


def _maximum_walkable_radius(environment: Environment, point: pygame.Vector2) -> int:
    """Maior raio inteiro livre no centro da rota, usando a máscara real."""
    upper = min(round(point.x), round(point.y), environment.size[0] - round(point.x) - 1, environment.size[1] - round(point.y) - 1)
    low, high = 0, max(0, upper)
    while low < high:
        candidate = (low + high + 1) // 2
        if environment.is_walkable(point.x, point.y, candidate):
            low = candidate
        else:
            high = candidate - 1
    return low
