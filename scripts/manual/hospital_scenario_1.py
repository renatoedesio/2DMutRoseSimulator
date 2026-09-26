"""Inicia o cenário 1 do Hospital."""

from src.scenarios import HOSPITAL_SCENARIO_1
from src.core.simulator import Simulator


if __name__ == "__main__":
    Simulator(HOSPITAL_SCENARIO_1).run()
