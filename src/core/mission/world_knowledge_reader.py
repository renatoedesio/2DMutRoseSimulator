"""Leitura do World DB XML independente do simulador."""

from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree


@dataclass(frozen=True)
class WorldRoom:
    name: str
    cell: str
    is_clean: bool
    is_prepared: bool
    door_open: bool


@dataclass(frozen=True)
class WorldKnowledge:
    rooms: dict[str, WorldRoom]


class WorldKnowledgeReader:
    """Converte o arquivo World_db.xml em estado lógico inicial do mundo."""

    def read(self, path: str | Path) -> WorldKnowledge:
        root = ElementTree.parse(path).getroot()
        rooms = {}
        for room_element in root.findall("Room"):
            name = self._value(room_element, "name")
            rooms[name] = WorldRoom(
                name=name,
                cell=self._value(room_element, "location"),
                is_clean=self._value(room_element, "is_clean").casefold() == "true",
                is_prepared=self._value(room_element, "is_prepared").casefold() == "true",
                door_open=self._value(room_element, "door_open").casefold() == "true",
            )
        return WorldKnowledge(rooms)

    @staticmethod
    def _value(element: ElementTree.Element, name: str) -> str:
        child = element.find(name)
        return child.text.strip() if child is not None and child.text else ""
