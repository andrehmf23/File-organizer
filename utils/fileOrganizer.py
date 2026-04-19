from pathlib import Path
import shutil
from datetime import datetime
import os

# Formatar para identificação de data
DATE_FORMAT = {
    'y': '%Y',
    'm': '%m',
    'd': '%d'
}

class FileOrganizer:
    """Organiza arquivos automaticamente
    
    Identifica os arquivos no caminho alvo e depois de passar 
    por filtros move-os ou copia-os para o caminho destinado.
    """

    def __init__(
        self,
        target: str, # Caminho alvo
        destination: str, # Caminho destinado
        level_limit: int | None = None,
        copy: bool = True,
        structure: str = None,
        show: bool = False
    ):
        """
        Args:
            target: Caminho de origem dos arquivos.
            destination: Caminho onde os arquivos serão organizados.
            level_limit: Limite de profundidade de busca.
            copy: Se True, copia; se False, move.
            structure: Define a estrutura de pastas.
            show: Ativa print de progresso.

            Identificadores do structure:
                'a' -> Alfabético
                'y' / 'm' / 'd' -> Ano, Mês, Dia
                't' -> Data
                's' -> Sufixo (Extensão)
        """

        self.target: Path = Path(target)

        if not self.target.exists():
            raise ValueError("target does not exist!")

        self.destination = Path(destination)

        if not self.destination.exists():
            self.destination.mkdir(parents=True, exist_ok=True)
        
        self.level_limit = level_limit
        self.copy = copy

        self.structure = structure.lower() if structure else None
        
        # Filtro de busca
        self.filter = {
            "name": None,
            "type": None,
            "date": None
        }

        self.show = show

        # Variáveis temporárias
        self._destination_resolve = self.destination.resolve()

        # Contadores do progresso
        self.count_max = self._count_files(self.target)
        self.count_proportional = max(1, self.count_max // 100)
        self.count_current = 0


    
    def _count_files(self, current: Path, level: int = 0):
        if self.level_limit is not None and level > self.level_limit:
            return 0

        counter = 0

        for item in current.iterdir():
            if item.is_file():
                counter += 1
            else:
                if item.resolve() == self._destination_resolve:
                    continue
                counter += self._count_files(item, level + 1)

        return counter

    
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
    
    def collect(self):

        # Evita chamadas desnecessárias ao stat (melhora performance)
        needs_stat = (
            self.filter["date"] is not None or
            (self.structure and any(c in self.structure for c in "ymdt"))
        )

        self._collect(self.target, needs_stat)

        if self.show:
            print(f"\nFinalizado [{self.count_current}/{self.count_max}]")
    
    def _collect(self, current: Path, needs_stat: bool, level: int = 0):
        """Percorre recursivamente diretórios coletando arquivos que atendem aos filtros."""

        if self.level_limit is not None and level > self.level_limit:
            return

        for item in current.iterdir():
            if item.is_file():
                self.count_current += 1
                if self.show and self.count_current % self.count_proportional == 0:
                    print(f"Progresso [{self.count_current}/{self.count_max}]", end="\r")

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

            else:

                if item.resolve() == self._destination_resolve:
                    continue

                self._collect(item, needs_stat, level + 1)
    
    def _single_files(self, destination: Path) -> Path:
        """Gera um novo caminho único caso o arquivo já exista no destino."""
        if not destination.exists():
            return destination

        save_destination = destination
        i = 1
        while destination.exists():
            destination = save_destination.with_stem(f"{save_destination.stem}_{i}")
            i += 1

        return destination
    
    # Estrutura o caminho com pastas
    def _structured_path(self, target: Path, destination: Path, stat: os.stat_result):
        """
        Constrói o caminho de destino baseado na string `structure`.

        Exemplo:
            'ymd' -> /2024/03/15
            'as'  -> /A/txt
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

        # Estrutura caminho
        if self.structure:
            destination = self._structured_path(target, destination, stat)
        
        destination.mkdir(parents=True, exist_ok=True)

        # Evita sobrescrita
        destination = self._single_files(destination / target.name)

        # Copiar ou mover
        if self.copy:
            shutil.copy2(target, destination)
        else:
            shutil.move(target, destination)
