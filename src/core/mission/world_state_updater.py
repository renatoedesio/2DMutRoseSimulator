"""Serializa o estado observado do Hospital para o World DB do MutROSe."""

from pathlib import Path
from xml.etree.ElementTree import Element, ElementTree, SubElement


class WorldStateUpdater:
    def write_hospital(self, domain, path: Path) -> None:
        root = Element("world_db")
        for name, state in domain.rooms.items():
            room = SubElement(root, "Room")
            SubElement(room, "name").text = name
            SubElement(room, "location").text = {"RoomA": "c3", "RoomB": "c6", "RoomC": "c8", "SanitizationRoom": "c10"}[name]
            for attribute in (
                "is_clean", "is_prepared", "door_open", "door_operational", "accessible", "alternate_access",
                "standard_cleaning_available", "backup_cleaning_available",
                "standard_organization_available", "alternative_organization_available",
            ):
                SubElement(room, attribute).text = str(getattr(state, attribute, False))
        path.parent.mkdir(parents=True, exist_ok=True)
        ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
