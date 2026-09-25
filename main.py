"""Inicializa o simulador robótico 2D."""

from src.simulator import Simulator
from src.scenarios import HOSPITAL


if __name__ == "__main__":
    Simulator(HOSPITAL).run()
