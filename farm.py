"""Inicia o cenário Fazenda."""

from src.scenarios import FARM
from src.simulator import Simulator


if __name__ == "__main__":
    Simulator(FARM).run()
