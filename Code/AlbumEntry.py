from dataclasses import dataclass

NEW = "New"
CHECKED = "Checked"


@dataclass
class AlbumEntry:
    band: str = None
    title: str = None
    year: str = None
    url: str = None
    listened: str = NEW
