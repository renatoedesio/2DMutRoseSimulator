"""Ciclo principal do simulador a 60 quadros por segundo."""

from pathlib import Path

import pygame

from src.behavior_tree import NavigationController
from src.command_console import CommandConsole
from src.environment import Environment
from src.robot import Robot
from src.scenarios import Scenario


class Simulator:
    """Coordena eventos, atualização e renderização do ambiente robótico."""

    FPS = 60
    WINDOW_SIZE = (1280, 800)

    def __init__(self, scenario: Scenario) -> None:
        pygame.init()
        pygame.display.set_caption(f"Simulador Robótico 2D - {scenario.title}")
        self.screen = pygame.display.set_mode(self.WINDOW_SIZE)
        self.clock = pygame.time.Clock()

        project_directory = Path(__file__).resolve().parent.parent
        self.environment = Environment(project_directory / "assets" / scenario.asset_folder, self.WINDOW_SIZE, scenario)
        self.screen = pygame.display.set_mode(self.environment.size)
        self.robots = [Robot(definition) for definition in scenario.robots]
        self.navigations = [NavigationController(robot, self.environment) for robot in self.robots]
        self.selected_robot_index = 0
        self.command_console = CommandConsole()
        self.mission_dispatcher = None
        self.font = pygame.font.Font(None, 28)
        self.running = True

    def run(self) -> None:
        self.command_console.start()
        while self.running:
            delta_time = self.clock.tick(self.FPS) / 1000
            self._handle_events()
            self._handle_console_commands()
            if self.mission_dispatcher is not None:
                self.mission_dispatcher.update(delta_time)
            for navigation in self.navigations:
                navigation.tick(delta_time)
            self._render()

        pygame.quit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                self._select_robot(-1)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                self._select_robot(1)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.selected_navigation.set_target_point(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
                self._erase_injected_obstacle(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                self._inject_obstacle(event.pos)
            elif event.type == pygame.MOUSEMOTION and event.buttons[1]:
                self._erase_injected_obstacle(event.pos)
            elif event.type == pygame.MOUSEMOTION and event.buttons[2]:
                self._inject_obstacle(event.pos)

    def _inject_obstacle(self, position: tuple[int, int]) -> None:
        self.environment.add_injected_obstacle(position)

    def _erase_injected_obstacle(self, position: tuple[int, int]) -> None:
        self.environment.remove_injected_obstacle(position)

    def set_mission_dispatcher(self, dispatcher) -> None:
        self.mission_dispatcher = dispatcher

    @property
    def selected_robot(self) -> Robot:
        return self.robots[self.selected_robot_index]

    @property
    def selected_navigation(self) -> NavigationController:
        return self.navigations[self.selected_robot_index]

    def _select_robot(self, direction: int) -> None:
        self.selected_robot_index = (self.selected_robot_index + direction) % len(self.robots)

    def _handle_console_commands(self) -> None:
        command = self.command_console.get_next_command()
        while command is not None:
            self._execute_command(command)
            command = self.command_console.get_next_command()

    def _execute_command(self, command: str) -> None:
        parts = command.split()
        if not parts or parts[0].casefold() != "goto" or len(parts) not in (2, 3):
            print("Comando inválido. Use: goto <sala> ou goto <robô> <sala>")
            return

        navigation = self.selected_navigation
        if len(parts) == 3:
            robot = next((item for item in self.robots if item.label.casefold() == parts[1].casefold()), None)
            if robot is None:
                print("Robô não encontrado.")
                return
            navigation = self.navigations[self.robots.index(robot)]
            destination_name = parts[2]
        else:
            destination_name = parts[1]

        location = self.environment.get_location_by_name(destination_name)
        if location is None:
            available = ", ".join(location.name for location in self.environment.locations)
            print(f"Local não encontrado. Disponíveis: {available}")
            return

        navigation.set_target(location)
        print(f"{navigation.context.robot.label} indo para {location.name}.")

    def _render(self) -> None:
        self.environment.draw(self.screen)
        for robot, navigation in zip(self.robots, self.navigations):
            target = navigation.target
            target_point = pygame.Vector2(target.center) if target else None
            robot.draw_route(self.screen, navigation.waypoints, target_point)
        for index, robot in enumerate(self.robots):
            robot.draw(self.screen, self.font, index == self.selected_robot_index)
        self._draw_location_label()
        self._draw_navigation_error()
        self._draw_mission_status()
        self._draw_controls_hint()
        pygame.display.flip()

    def _draw_location_label(self) -> None:
        location = self.environment.get_location(self.selected_robot.position)
        name = location.name if location else "Área não identificada"
        label = self.font.render(
            f"{self.selected_robot.label} {self.selected_robot.role} | {self.selected_robot.state.value} {self.selected_robot.battery:.0f}% | {self.selected_robot.current_task} | {name}",
            True,
            (20, 35, 45),
        )
        background = label.get_rect(topleft=(12, 12)).inflate(16, 12)
        pygame.draw.rect(self.screen, (255, 255, 255), background, border_radius=5)
        pygame.draw.rect(self.screen, (120, 140, 150), background, 1, border_radius=5)
        self.screen.blit(label, (20, 18))

    def _draw_navigation_error(self) -> None:
        error = self.selected_navigation.error_message
        if error is None:
            return
        label = self.font.render(error, True, (255, 255, 255))
        background = label.get_rect(topleft=(12, 56)).inflate(16, 12)
        pygame.draw.rect(self.screen, (192, 57, 43), background, border_radius=5)
        self.screen.blit(label, (20, 62))

    def _draw_mission_status(self) -> None:
        if self.mission_dispatcher is None:
            return
        label = self.font.render(self.mission_dispatcher.status_text, True, (20, 35, 45))
        background = label.get_rect(topright=(self.screen.get_width() - 12, 12)).inflate(16, 12)
        pygame.draw.rect(self.screen, (255, 255, 255), background, border_radius=5)
        pygame.draw.rect(self.screen, (120, 140, 150), background, 1, border_radius=5)
        self.screen.blit(label, (background.x + 8, background.y + 6))

    def _draw_controls_hint(self) -> None:
        hint = self.font.render(
            "SETA CIMA / SETA BAIXO: trocar robô | Direito: injetar | Meio: apagar",
            True,
            (20, 35, 45),
        )
        background = hint.get_rect(
            bottomright=(self.screen.get_width() - 12, self.screen.get_height() - 12)
        ).inflate(16, 12)
        pygame.draw.rect(self.screen, (255, 255, 255), background, border_radius=5)
        pygame.draw.rect(self.screen, (120, 140, 150), background, 1, border_radius=5)
        self.screen.blit(hint, (background.x + 8, background.y + 6))
