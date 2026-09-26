"""Recria o mapa de exemplo Hospital a partir da configuração atual."""

from pathlib import Path

import pygame

from src.environment import Environment
from src.scenarios import HOSPITAL_SCENARIO_1
from src.simulator import Simulator


def main() -> None:
    pygame.init()
    pygame.display.set_mode((1, 1), flags=pygame.HIDDEN)
    project_directory = Path(__file__).resolve().parent.parent.parent
    environment = Environment(
        project_directory / "assets" / HOSPITAL_SCENARIO_1.asset_folder,
        Simulator.WINDOW_SIZE,
        HOSPITAL_SCENARIO_1,
    )
    environment.regenerate_example_assets(Simulator.WINDOW_SIZE)
    pygame.quit()
    print("Mapa Hospital recriado com RoomA, RoomB, RoomC e SanitizationRoom.")


if __name__ == "__main__":
    main()
