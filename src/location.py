"""Definição de áreas lógicas identificadas por cores."""

from dataclasses import dataclass

import pygame


@dataclass(frozen=True)
class Location:
    """Uma sala ou corredor identificado por nome, cor e centro."""

    name: str
    color: tuple[int, int, int]
    center: tuple[int, int]
