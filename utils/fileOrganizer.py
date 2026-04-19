from pathlib import Path
import shutil
from datetime import datetime
import os

# ----------------------------
# Presets e formatos de data
# ----------------------------

DATE_FORMAT = {
    'y': '%Y',
    'm': '%m',
    'd': '%d'
}


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
        copy: bool = True, # Copiar arquivos, caso contrario os move
        structure: str = None, # Opcional
    ):
        self.target = Path(target)
        self.destination = Path(destination)
        
        self.level_limit = level_limit
        self.copy = copy

        self.structure = structure.lower() if structure else None
        
        # Filtros de busca
        self.filter = {
            "name": None,
            "type": None,
            "date": None
        }

        self.destination.mkdir(parents=True, exist_ok=True)

        # Variáveis temporárias
        self._destination_resolve = self.destination.resolve()
        
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
    
    # ----------------------------
    # Coleta recursiva
    # ----------------------------
    # Encontra multiplos arquivos e pasta de um diretório
    # Se pasta, entra dentro dela
    # Se arquivo, filtra e envia para organize

    def collect(self):

        # Otimização do stat do Path
        needs_stat = (
            self.filter["date"] is not None or
            (self.structure and any(c in self.structure for c in "ymdt"))
        )

        self._collect(self.target, needs_stat)

    def _collect(self, current: Path, needs_stat: bool, level: int = 0):

        if self.level_limit is not None and level > self.level_limit:
            return

        for item in current.iterdir():
            if item.is_file():
                
                if self.filter["name"] is not None and self.filter["name"] not in item.name:
                    continue

                if self.filter["type"] is not None and self.filter["type"] != item.suffix.lower().lstrip('.'):
                    continue

                # Otimização do stat
                stat = item.stat() if needs_stat else None
                
                if self.filter["date"] is not None:
                    start, end = self.filter["date"]
                    if not (start <= stat.st_mtime <= end):
                        continue

                self._organize(item, self.destination, stat)

            elif item.is_dir():

                if item.resolve() == self._destination_resolve:
                    continue

                self._collect(item, needs_stat, level + 1)
    
    # ----------------------------
    # Caminho único
    # ----------------------------
    # Reescreve o caminho para ser único se necessário

    def _single_files(self, destination: Path) -> Path:

        # Assume que já está criado

        i = 1
        while True:
            new_destination = destination.with_stem(f"{destination.stem}_{i}")
            if not new_destination.exists():
                return new_destination
            i += 1

    # ----------------------------
    # Organização
    # ----------------------------

    def _structured_path(self, target: Path, destination: Path, stat: os.stat_result):

        """
        Estrutura o caminho do destino deacordo com o comandos do structure
        """

        date = None

        for command in self.structure:

            # Alfabético
            if command == 'a':
                c = next((ch for ch in target.name if ch.isalpha()), '#').upper()
                destination /= c

            # Dia, Mês ou ano
            elif command in ('y','m','d'):
                if date is None:
                    date = datetime.fromtimestamp(stat.st_mtime)
                destination /= date.strftime(DATE_FORMAT[command])
                
            # Data (Time)
            elif command == 't':
                if date is None:
                    date = datetime.fromtimestamp(stat.st_mtime)
                destination /= date.strftime("%Y-%m-%d")

            # Sufixo
            elif command == 's':
                suffix = target.suffix.lower().lstrip('.') or 'WITHOUT_SUFFIX'
                destination /= suffix

            # LANGUAGE -> Under contruction

        return destination

    def _organize(self, target: Path, destination: Path, stat: os.stat_result):

        # Estrutura caminho se uma estrutura existir
        if self.structure:
            destination = self._structured_path(target, destination, stat)

        # Cria diretórios
        destination.mkdir(parents=True, exist_ok=True)

        # Evita sobrescrita
        destination = self._single_files(destination / target.name)

        # Copiar ou mover
        if self.copy:
            shutil.copy2(target, destination)
        else:
            shutil.move(target, destination)
