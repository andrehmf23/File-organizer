from pathlib import Path
import shutil
from enum import Enum
from datetime import datetime
import math


# ----------------------------
# Presets e formatos de data
# ----------------------------

DATE_FORMAT = {
    'y': '%Y',
    'm': '%m',
    'd': '%d'
}

DATE_PRESETS = {
    "y":   ['y', '', ''],
    "m":   ['', 'm', ''],
    "d":   ['', '', 'd'],
    "ym":  ['y', 'm', ''],
    "md":  ['', 'm', 'd'],
    "ymd": ['y', 'm', 'd'],
}


# ----------------------------
# Enum de organização
# ----------------------------

class Organizer(Enum):
    DIRECT = 0
    ALPHABETICAL = 1
    DATE = 2
    SUFFIX = 3


# ----------------------------
# Classe principal
# ----------------------------

class FileOrganizer:
    def __init__(
        self,
        target: str,
        destination: str,
        level_limit: int = math.inf,
        copy: bool = True,
        organizer: Organizer = Organizer.DIRECT,
        date_tree: bool = False,
        date_preset: str = "ymd"
    ):
        self.target = Path(target)
        self.destination = Path(destination)
        self.level_limit = level_limit
        self.copy = copy

        self.organizer = organizer
        self.date_tree = date_tree

        # Filtros
        self.filter = {
            "name": "",
            "type": "",
            "date": []
        }

        # Preset de data
        date_preset = date_preset.lower()
        if date_preset not in DATE_PRESETS:
            raise ValueError(f"Preset de data inválido: {date_preset}")

        self.date_order = DATE_PRESETS[date_preset]

        self.destination.mkdir(parents=True, exist_ok=True)

    # ----------------------------
    # Filtros
    # ----------------------------

    def set_filter(self, name="", type="", date_start="", date_end=""):
        self.filter["name"] = name
        self.filter["type"] = type

        if date_start and date_end:
            self.filter["date"] = [
                datetime.strptime(date_start, "%Y-%m-%d").timestamp(),
                datetime.strptime(date_end, "%Y-%m-%d").timestamp()
            ]
        else:
            self.filter["date"] = []

    # ----------------------------
    # Evitar sobrescrita
    # ----------------------------

    def unique_dest(self, dest: Path) -> Path:
        if not dest.exists():
            return dest

        i = 1
        while True:
            new_dest = dest.with_stem(f"{dest.stem}_{i}")
            if not new_dest.exists():
                return new_dest
            i += 1

    # ----------------------------
    # Coleta recursiva
    # ----------------------------

    def collect(self, current: Path = None, level: int = 0):
        if current is None:
            current = self.target

        if level > self.level_limit:
            return

        for item in current.iterdir():
            if item.is_file():
                mtime = item.stat().st_mtime

                if self.filter["name"] and item.name != self.filter["name"]:
                    continue

                if self.filter["type"] and item.suffix.lstrip('.') != self.filter["type"]:
                    continue

                if self.filter["date"]:
                    start, end = self.filter["date"]
                    if not (start <= mtime <= end):
                        continue

                self.organize(item)

            elif item.is_dir():
                if item.resolve() == self.destination.resolve():
                    continue
                self.collect(item, level + 1)

    # ----------------------------
    # Organização
    # ----------------------------

    def organize(self, item: Path):
        dest = self.destination

        # Alfabético
        if self.organizer == Organizer.ALPHABETICAL:
            c = next((ch for ch in item.name if ch.isalpha()), '#').upper()
            dest /= c

        # Data
        elif self.organizer == Organizer.DATE:
            date = datetime.fromtimestamp(item.stat().st_mtime)
            formats = [DATE_FORMAT[p] for p in self.date_order if p]

            if self.date_tree:
                for fmt in formats:
                    dest /= date.strftime(fmt)
            else:
                dest /= date.strftime("-".join(formats))

        # Sufixo
        elif self.organizer == Organizer.SUFFIX:
            suffix = item.suffix.lstrip('.').lower() or 'SEM_EXTENSAO'
            dest /= suffix

        # Cria diretórios
        dest.mkdir(parents=True, exist_ok=True)

        # Evita sobrescrita
        dest = self.unique_dest(dest / item.name)

        # Copiar ou mover
        if self.copy:
            shutil.copy2(item, dest)
        else:
            shutil.move(item, dest)
