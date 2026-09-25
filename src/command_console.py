"""Leitura não bloqueante de comandos digitados no terminal."""

from queue import Empty, Queue
from threading import Thread


class CommandConsole:
    """Recebe comandos do terminal sem interromper a janela do Pygame."""

    def __init__(self) -> None:
        self._commands: Queue[str] = Queue()

    def start(self) -> None:
        Thread(target=self._listen, daemon=True, name="command-console").start()

    def _listen(self) -> None:
        print("Comandos disponíveis: goto <nome da sala>. Exemplo: goto Sala_B")
        while True:
            try:
                command = input("comando> ").strip()
            except EOFError:
                return
            if command:
                self._commands.put(command)

    def get_next_command(self) -> str | None:
        try:
            return self._commands.get_nowait()
        except Empty:
            return None
