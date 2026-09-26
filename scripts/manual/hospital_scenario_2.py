"""Inicia o cenário 2 do Hospital."""

from src.scenarios import HOSPITAL_SCENARIO_2
from src.core.simulator import Simulator


if __name__ == "__main__":
    Simulator(HOSPITAL_SCENARIO_2).run()
