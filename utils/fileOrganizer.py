from pathlib import Path
import shutil
from enum import Enum, auto
from datetime import datetime
import unicodedata
import time

# ----------------------------
# Presets e formatos de data
# ----------------------------

DATE_FORMAT = {
    'y': '%Y',
    'm': '%m',
    'd': '%d'
}

# ----------------------------
# Enum de organização
# ----------------------------

class Organizer(Enum):
    DIRECT = auto()
    ALPHABETICAL = auto()
    DATE = auto()
    SUFFIX = auto()


# ----------------------------
# Classe principal
# ----------------------------

class FileOrganizer:
    """Organiza arquivos automaticamente
    
    Identifica os arquivos no caminho alvo e depois de passar 
    por filtros move-os ou copia-os para o caminho destinado
    """
    
    def __init__(
        self,
        target: str, # Caminho da coleta
        destination: str, # Caminho da organização
        level_limit: int | None = None, # Limite de leitura de profundidade
        copy: bool = True,
        organizer: Organizer = Organizer.DIRECT,
        language: str = None,
        date_tree: bool = False,
        data_order: str = "ymd"
    ):
        self.target = Path(target)
        self.destination = Path(destination)
        
        self.level_limit = level_limit
        self.copy = copy

        self.language = language

        self.organizer = organizer
        self.date_tree = date_tree

        # Preset de data
        self.date_order = data_order.lower()
        
        # Filtros
        self.filter = {
            "name": None,
            "type": None,
            "date": None
        }

        self.destination.mkdir(parents=True, exist_ok=True)
        
    # ----------------------------
    # Filtros
    # ----------------------------

    def set_filter(self, name=None, type=None, date_start=None, date_end=None):
        self.filter["name"] = name
        self.filter["type"] = type

        if date_start is not None and date_end is not None:
            self.filter["date"] = [
                datetime.strptime(date_start, "%Y-%m-%d").timestamp(),
                datetime.strptime(date_end, "%Y-%m-%d").timestamp()
            ]
        else:
            self.filter["date"] = None
    
    def detect_script(c):
        return unicodedata.name(c, '')

    # ----------------------------
    # Caminho único
    # ----------------------------
    # Reescreve o caminho para ser único se necessário

    def single_files(self, destination: Path) -> Path:
        if not destination.exists():
            return destination

        i = 1
        while True:
            new_destination = destination.with_stem(f"{destination.stem}_{i}")
            if not new_destination.exists():
                return new_destination
            i += 1
    
    # ----------------------------
    # Coleta recursiva
    # ----------------------------
    # Encontra multiplos arquivos e pasta de um diretório
    # Se pasta, entra dentro dela
    # Se arquivo, filtra e envia para organize

    def collect(self):
        self.__collect(self.target)

    def __collect(self, current: Path, level: int = 0):

        if self.level_limit is not None and level > self.level_limit:
            return
        
        for item in current.iterdir():
            if item.is_file():

                # Verificação do filtro
                if self.filter["name"] is not None and item.name != self.filter["name"]:
                    continue

                if self.filter["type"] is not None and item.suffix.lower().lstrip('.') != self.filter["type"]:
                    continue

                stat = item.stat()
                
                if self.filter["date"] is not None:
                    start, end = self.filter["date"]
                    if not (start <= stat.st_mtime <= end):
                        continue

                start = time.perf_counter()

                self.organize(item, stat)

                end = time.perf_counter()
                sub = end - start
                if sub > 0.1: print(f"Tempo de organize: {sub:.6f} segundos [{item}]")

            elif item.is_dir():
                # Impede o acesso do caminho de organização
                if item.resolve() == self.destination.resolve():
                    continue
                self.__collect(item, level + 1)

    # ----------------------------
    # Organização
    # ----------------------------

    def organize(self, item: Path, stat):
        destination = self.destination

        # Alfabético
        if self.organizer == Organizer.ALPHABETICAL:
            c = next((ch for ch in item.name if ch.isalpha()), '#').upper()

            if self.language is None:
                destination /= c
            elif self.language == self.detect_script(c):
                destination /= c
            else:
                destination /= 'others'

        # Data
        elif self.organizer == Organizer.DATE:
            date = datetime.fromtimestamp(stat.st_mtime)
            formats = [DATE_FORMAT[p] for p in self.date_order if p in DATE_FORMAT]

            if self.date_tree:
                for format in formats:
                    destination /= date.strftime(format)
            else:
                destination /= date.strftime("-".join(formats))

        # Sufixo
        elif self.organizer == Organizer.SUFFIX:
            suffix = item.suffix.lstrip('.').lower() or 'SEM_EXTENSAO'
            destination /= suffix

        # Cria diretórios
        destination.mkdir(parents=True, exist_ok=True)

        # Evita sobrescrita
        destination = self.single_files(destination / item.name)

        # Copiar ou mover
        if self.copy:
            shutil.copy2(item, destination)
        else:
            shutil.move(item, destination)
