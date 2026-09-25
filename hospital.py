"""Inicia o cenário Hospital."""

from src.scenarios import HOSPITAL_SCENARIO_1
from src.simulator import Simulator


if __name__ == "__main__":
    Simulator(HOSPITAL_SCENARIO_1).run()
